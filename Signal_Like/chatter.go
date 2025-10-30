// Implementation of a forward-secure, end-to-end encrypted messaging client
// supporting key compromise recovery and out-of-order message delivery.
// Directly inspired by Signal/Double-ratchet protocol but missing a few
// features. No asynchronous handshake support (pre-keys) for example.
//
// SECURITY WARNING: This code is meant for educational purposes and may
// contain vulnerabilities or other bugs. Please do not use it for
// security-critical applications.
//
// GRADING NOTES: This is the only file you need to modify for this assignment.
// You may add additional support files if desired. You should modify this file
// to implement the intended protocol, but preserve the function signatures
// for the following methods to ensure your implementation will work with
// standard test code:
//
// *NewChatter
// *EndSession
// *InitiateHandshake
// *ReturnHandshake
// *FinalizeHandshake
// *SendMessage
// *ReceiveMessage
//
// In addition, you'll need to keep all of the following structs' fields:
//
// *Chatter
// *Session
// *Message
//
// You may add fields if needed (not necessary) but don't rename or delete
// any existing fields.
//
// Original version
// Joseph Bonneau February 2019

package chatterbox

import (
	//	"bytes" //un-comment for helpers like bytes.equal
	"encoding/binary"
	"errors"
	//	"fmt" //un-comment if you want to do any debug printing.
)

// Labels for key derivation

// Label for generating a check key from the initial root.
// Used for verifying the results of a handshake out-of-band.
const HANDSHAKE_CHECK_LABEL byte = 0x11

// Label for ratcheting the root key after deriving a key chain from it
const ROOT_LABEL = 0x22

// Label for ratcheting the main chain of keys
const CHAIN_LABEL = 0x33

// Label for deriving message keys from chain keys
const KEY_LABEL = 0x44

// Chatter represents a chat participant. Each Chatter has a single long-term
// key Identity, and a map of open sessions with other users (indexed by their
// identity keys). You should not need to modify this.
type Chatter struct {
	Identity *KeyPair
	Sessions map[PublicKey]*Session
}

// Session represents an open session between one chatter and another.
// You should not need to modify this, though you can add additional fields
// if you want to.
type Session struct {
	MyDHRatchet       *KeyPair
	PartnerDHRatchet  *PublicKey
	RootChain         *SymmetricKey
	SendChain         *SymmetricKey
	ReceiveChain      *SymmetricKey
	CachedReceiveKeys map[int]*SymmetricKey
	SendCounter       int
	LastUpdate        int
	ReceiveCounter    int
}

// Message represents a message as sent over an untrusted network.
// The first 5 fields are send unencrypted (but should be authenticated).
// The ciphertext contains the (encrypted) communication payload.
// You should not need to modify this.
type Message struct {
	Sender        *PublicKey
	Receiver      *PublicKey
	NextDHRatchet *PublicKey
	Counter       int
	LastUpdate    int
	Ciphertext    []byte
	IV            []byte
}

// EncodeAdditionalData encodes all of the non-ciphertext fields of a message
// into a single byte array, suitable for use as additional authenticated data
// in an AEAD scheme. You should not need to modify this code.
func (m *Message) EncodeAdditionalData() []byte {
	buf := make([]byte, 8+3*FINGERPRINT_LENGTH)

	binary.LittleEndian.PutUint32(buf, uint32(m.Counter))
	binary.LittleEndian.PutUint32(buf[4:], uint32(m.LastUpdate))

	if m.Sender != nil {
		copy(buf[8:], m.Sender.Fingerprint())
	}
	if m.Receiver != nil {
		copy(buf[8+FINGERPRINT_LENGTH:], m.Receiver.Fingerprint())
	}
	if m.NextDHRatchet != nil {
		copy(buf[8+2*FINGERPRINT_LENGTH:], m.NextDHRatchet.Fingerprint())
	}

	return buf
}

// NewChatter creates and initializes a new Chatter object. A long-term
// identity key is created and the map of sessions is initialized.
// You should not need to modify this code.
func NewChatter() *Chatter {
	c := new(Chatter)
	c.Identity = GenerateKeyPair()
	c.Sessions = make(map[PublicKey]*Session)
	return c
}

// This is a helper to safely compare two public keys.
// It handles nil pointers and compares fingerprints for equality.
func areKeysIdentical(keyA, keyB *PublicKey) bool {
	if keyA == nil && keyB == nil {
		return true // Both are nil, so "identical" in this context
	}
	if keyA == nil || keyB == nil {
		return false // One is nil, the other isn't
	}

	// Compare the fingerprints byte by byte
	fingerprintA := keyA.Fingerprint()
	fingerprintB := keyB.Fingerprint()
	if len(fingerprintA) != len(fingerprintB) {
		return false // Should never happen, but good to check
	}
	for i := range fingerprintA {
		if fingerprintA[i] != fingerprintB[i] {
			return false
		}
	}
	return true
}

// this safely zeroizes the main symmetric keys in a session.
func zeroizeSessionChains(s *Session) {
	if s.RootChain != nil {
		s.RootChain.Zeroize()
		s.RootChain = nil
	}
	if s.SendChain != nil {
		s.SendChain.Zeroize()
		s.SendChain = nil
	}
	if s.ReceiveChain != nil {
		s.ReceiveChain.Zeroize()
		s.ReceiveChain = nil
	}
}

// this iterates over the key cache and zeroizes every stored key.
func deletesCachedKeys(cache map[int]*SymmetricKey) {
	if cache == nil {
		return
	}
	for index, storedKey := range cache {
		if storedKey != nil {
			storedKey.Zeroize()
		}
		delete(cache, index) // Remove the entry from the map
	}
}

// EndSession erases all data for a session with the designated partner.
// All outstanding key material should be zeroized and the session erased.
func (c *Chatter) EndSession(partnerIdentity *PublicKey) error {

	if _, exists := c.Sessions[*partnerIdentity]; !exists {
		return errors.New("Don't have that session open to tear down")
	}

	// Get the session we're about to destroy
	sessionToClose := c.Sessions[*partnerIdentity]

	// Securely wipe all symmetric key material
	zeroizeSessionChains(sessionToClose)
	deletesCachedKeys(sessionToClose.CachedReceiveKeys)

	// Securely wipe our own DH ratchet keypair
	if sessionToClose.MyDHRatchet != nil {
		sessionToClose.MyDHRatchet.Zeroize()
		sessionToClose.MyDHRatchet = nil
	}

	// Nil out all other fields to be safe
	sessionToClose.PartnerDHRatchet = nil
	sessionToClose.CachedReceiveKeys = nil
	sessionToClose.SendCounter = 0
	sessionToClose.ReceiveCounter = 0
	sessionToClose.LastUpdate = 0

	// Finally, remove the session from the chatter's map
	delete(c.Sessions, *partnerIdentity)

	return nil
}

// InitiateHandshake prepares the first message sent in a handshake, containing
// an ephemeral DH share. The partner which calls this method is the initiator.
func (c *Chatter) InitiateHandshake(partnerIdentity *PublicKey) (*PublicKey, error) {

	if _, exists := c.Sessions[*partnerIdentity]; exists {
		return nil, errors.New("Already have session open")
	}

	// We are the initiator. We generate a new ephemeral keypair for this handshake.
	initiatorEphemeral := GenerateKeyPair()

	// Create the new session object and store it.
	newSession := &Session{
		MyDHRatchet:       initiatorEphemeral, // This is our 'E' in the X3DH
		PartnerDHRatchet:  nil,                // We don't know the partner's ephemeral key yet
		RootChain:         nil,                // Not established yet
		SendChain:         nil,                // Not established yet
		ReceiveChain:      nil,                // Not established yet
		CachedReceiveKeys: make(map[int]*SymmetricKey),
		SendCounter:       0,
		LastUpdate:        1, // We set this to 1 as the initiator
		ReceiveCounter:    0,
	}
	c.Sessions[*partnerIdentity] = newSession

	// Return our new public ephemeral key to be sent to the partner.
	return &initiatorEphemeral.PublicKey, nil
}

// This computes the initial root key using the
// "Triple DH" (X3DH) key agreement for the responding user.
func calculateSharedSecretForResponder(myID *KeyPair, myEph *KeyPair,
	partnerID *PublicKey, partnerEph *PublicKey) *SymmetricKey {

	// The responder performs three DH calculations:
	// 1. (Partner Identity, My Ephemeral)
	dhResult1 := DHCombine(partnerID, &myEph.PrivateKey)
	// 2. (Partner Ephemeral, My Identity)
	dhResult2 := DHCombine(partnerEph, &myID.PrivateKey)
	// 3. (Partner Ephemeral, My Ephemeral)
	dhResult3 := DHCombine(partnerEph, &myEph.PrivateKey)

	// The final shared secret is a combination of all three.
	return CombineKeys(dhResult1, dhResult2, dhResult3)
}

// ReturnHandshake prepares the second message sent in a handshake, containing
// an ephemeral DH share. The partner which calls this method is the responder.
func (c *Chatter) ReturnHandshake(partnerIdentity,
	partnerEphemeral *PublicKey) (*PublicKey, *SymmetricKey, error) {

	if _, exists := c.Sessions[*partnerIdentity]; exists {
		return nil, nil, errors.New("Already have session open")
	}

	// We are the responder. We also generate a new ephemeral keypair.
	responderEphemeral := GenerateKeyPair()

	// Calculate the initial shared secret (root key)
	masterSecret := calculateSharedSecretForResponder(c.Identity, responderEphemeral,
		partnerIdentity, partnerEphemeral)

	// Create and store the new session state.
	c.Sessions[*partnerIdentity] = &Session{
		MyDHRatchet:       responderEphemeral,
		PartnerDHRatchet:  partnerEphemeral, // We know the initiator's ephemeral key
		RootChain:         masterSecret,
		SendChain:         nil,                // Responder can't send until initiator finalizes
		ReceiveChain:      masterSecret.Duplicate(),  // Ready to receive messages
		CachedReceiveKeys: make(map[int]*SymmetricKey),
		SendCounter:       0,
		LastUpdate:        0,
		ReceiveCounter:    0,
	}
	
	// We also derive a check key for out-of-band verification
	handshakeCheckKey := masterSecret.DeriveKey(HANDSHAKE_CHECK_LABEL)

	// Return our ephemeral key and the check key.
	return &responderEphemeral.PublicKey, handshakeCheckKey, nil
}

// THis computes the initial root key using the
// "Triple DH" (X3DH) key agreement for the initiating user.
func calculateSharedSecretForInitiator(myID *KeyPair, myEph *KeyPair,
	partnerID *PublicKey, partnerEph *PublicKey) *SymmetricKey {

	// The initiator performs a similar set of three DH calculations:
	// 1. (Partner Ephemeral, My Identity)
	dhResult1 := DHCombine(partnerEph, &myID.PrivateKey)
	// 2. (Partner Identity, My Ephemeral)
	dhResult2 := DHCombine(partnerID, &myEph.PrivateKey)
	// 3. (Partner Ephemeral, My Ephemeral)
	dhResult3 := DHCombine(partnerEph, &myEph.PrivateKey)

	// The final shared secret is a combination of all three.
	return CombineKeys(dhResult1, dhResult2, dhResult3)
}

// FinalizeHandshake lets the initiator receive the responder's ephemeral key
// and finalize the handshake.The partner which calls this method is the initiator.
func (c *Chatter) FinalizeHandshake(partnerIdentity,
	partnerEphemeral *PublicKey) (*SymmetricKey, error) {

	session := c.Sessions[*partnerIdentity]
	if _, exists := c.Sessions[*partnerIdentity]; !exists{
		return nil, errors.New("Can't finalize session, not yet open")
	}

	// We now have the responder's ephemeral key.
	session.PartnerDHRatchet = partnerEphemeral

	// Calculate the initial shared secret (root key).
	// This must match the one the responder calculated.
	masterSecret := calculateSharedSecretForInitiator(c.Identity, session.MyDHRatchet,
		partnerIdentity, partnerEphemeral)

	// Now we can fully populate the session state.
	session.RootChain = masterSecret
	session.SendChain = masterSecret.Duplicate()    // Ready to send
	session.ReceiveChain = masterSecret.Duplicate() // Ready to receive
	session.SendCounter = 0
	session.ReceiveCounter = 0
	// LastUpdate remains 1 from initialization

	// Derive the check key to verify with the partner.
	handshakeCheckKey := masterSecret.DeriveKey(HANDSHAKE_CHECK_LABEL)
	return handshakeCheckKey, nil
}

// This performs a sender-side Diffie-Hellman ratchet.
// This generates a new sending chain and updates the root chain.
func advanceSenderKeys(s *Session) {
	// 1. Generate a fresh ephemeral keypair for this ratchet step.
	newSenderEphemeral := GenerateKeyPair()

	// 2. Derive a "base" for the next root key from the current one.
	nextRootBase := s.RootChain.DeriveKey(ROOT_LABEL)

	// 3. Perform a DH between our new private key and our partner's last public key.
	dhOutput := DHCombine(s.PartnerDHRatchet, &newSenderEphemeral.PrivateKey)

	// 4. Combine the base and the DH output to create the new RootChain key.
	newRootChainKey := CombineKeys(nextRootBase, dhOutput)

	// 5. Clean up old keys and update the session state.
	if s.MyDHRatchet != nil {
		s.MyDHRatchet.Zeroize() // Zeroize the old private key
	}
	s.MyDHRatchet = newSenderEphemeral // Store the new keypair

	s.RootChain.Zeroize()
	s.RootChain = newRootChainKey
	s.SendChain = newRootChainKey.Duplicate() // This is our new SendChain

	// Record the message counter at which this update happened.
	s.LastUpdate = s.SendCounter + 1
}

// SendMessage is used to send the given plaintext string as a message.
// You'll need to implement the code to ratchet, derive keys and encrypt this message.
func (c *Chatter) SendMessage(partnerIdentity *PublicKey,
	plaintext string) (*Message, error) {

	session := c.Sessions[*partnerIdentity]
	if _, exists := c.Sessions[*partnerIdentity]; !exists {
		return nil, errors.New("Can't send message to partner with no open session")
	}

	// This is the message object we will populate and return.
	message := &Message{
		Sender:   &c.Identity.PublicKey,
		Receiver: partnerIdentity,
		// TODO: your code here
	}

	// If our SendChain is nil, it means we just completed a receive-side
	// ratchet and need to perform our own send-side ratchet before we can send.
	if session.SendChain == nil {
		advanceSenderKeys(session)
	}

	// This message will be sent with our current ratchet public key.
	message.NextDHRatchet = &session.MyDHRatchet.PublicKey

	// Increment the send counter for this message.
	session.SendCounter++
	message.Counter = session.SendCounter
	message.LastUpdate = session.LastUpdate // Record the last time we ratcheted.

	// --- Key Derivation ---
	// 1. Ratchet the SendChain to get the next SendChain key.
	nextSendChainKey := session.SendChain.DeriveKey(CHAIN_LABEL)
	session.SendChain.Zeroize() // Zeroize the old one
	session.SendChain = nextSendChainKey

	// 2. Derive the actual message encryption key from the new SendChain key.
	messageKey := session.SendChain.DeriveKey(KEY_LABEL)

	// --- Encryption ---
	iv := NewIV()
	aad := message.EncodeAdditionalData() // Get Additional Authenticated Data
	ciphertext := messageKey.AuthenticatedEncrypt(plaintext, aad, iv)
	message.Ciphertext = ciphertext
	message.IV = iv

	// Clean up the single-use message key.
	messageKey.Zeroize()

	return message, nil
}

// precomputeSkippedMessageKeys advances the receive chain to fill the cache
// with keys for messages that might arrive out of order.
func precomputeSkippedMessageKeys(s *Session, fromCounter, toCounter int) {
	// This loop "catches up" the receive chain, deriving each message
	// key along the way and storing it in the cache.
	for i := fromCounter; i < toCounter; i++ {
		// 1. Ratchet the chain
		nextReceiveChainKey := s.ReceiveChain.DeriveKey(CHAIN_LABEL)
		s.ReceiveChain.Zeroize()
		s.ReceiveChain = nextReceiveChainKey

		// 2. Derive and cache the message key
		s.CachedReceiveKeys[i] = s.ReceiveChain.DeriveKey(KEY_LABEL)
	}
	s.ReceiveCounter = toCounter - 1
}

// advanceReceiveKeys advances the receive chain to a specific target counter,
// caching all intermediate keys.
func advanceReceiveKeys(s *Session, targetCount int) {
	// This is used when we receive a message that is ahead of our current counter.
	for i := s.ReceiveCounter + 1; i <= targetCount; i++ {
		// 1. Ratchet the chain
		nextReceiveChainKey := s.ReceiveChain.DeriveKey(CHAIN_LABEL)
		s.ReceiveChain.Zeroize()
		s.ReceiveChain = nextReceiveChainKey

		// 2. Derive and cache the message key
		s.CachedReceiveKeys[i] = s.ReceiveChain.DeriveKey(KEY_LABEL)
	}
	s.ReceiveCounter = targetCount
}

// advanceReceiveRachet performs a receiver-side Diffie-Hellman ratchet.
// This happens when we receive a message with a new ratchet key from our partner.
func advanceReceiveRachet(s *Session, partnersNewRatchetKey *PublicKey) {
	// 1. Derive the "base" for the next root key from our current one.
	nextRootBase := s.RootChain.DeriveKey(ROOT_LABEL)

	// 2. Perform a DH between the new partner key and our current private key.
	dhOutput := DHCombine(partnersNewRatchetKey, &s.MyDHRatchet.PrivateKey)

	// 3. Combine them to create the new RootChain key.
	newRootChainKey := CombineKeys(nextRootBase, dhOutput)

	// 4. Update session state.
	s.RootChain.Zeroize()
	s.RootChain = newRootChainKey

	s.ReceiveChain.Zeroize()
	s.ReceiveChain = newRootChainKey.Duplicate() // This is our new ReceiveChain
	s.PartnerDHRatchet = partnersNewRatchetKey   // Store the new partner key
}

// THis reverts session state to a backup snapshot.
// This is crucial if decryption fails, ensuring the session state remains consistent.
func rollbackSessionStateAfterError(s *Session, snapshotPartnerKey *PublicKey,
	snapshotRoot, snapshotReceive *SymmetricKey, snapshotCounter int, failedMessageNum int) {

	// Restore the keys from the snapshots
	s.RootChain.Zeroize()
	s.ReceiveChain.Zeroize()
	s.RootChain = snapshotRoot
	s.ReceiveChain = snapshotReceive
	s.PartnerDHRatchet = snapshotPartnerKey

	// We also need to purge any keys we might have added to the cache
	// during this failed attempt.
	for i := snapshotCounter + 1; i <= failedMessageNum; i++ {
		if keyToWipe := s.CachedReceiveKeys[i]; keyToWipe != nil {
			keyToWipe.Zeroize()
		}
		delete(s.CachedReceiveKeys, i)
	}
	s.ReceiveCounter = snapshotCounter
}

// ReceiveMessage is used to receive the given message and return the correct
// plaintext. This method is where most of the key derivation, ratcheting
// and out-of-order message handling logic happens.
func (c *Chatter) ReceiveMessage(message *Message) (string, error) {

	session := c.Sessions[*message.Sender]
	if  _, exists := c.Sessions[*message.Sender]; !exists{
		return "", errors.New("Can't receive message from partner with no open session")
	}

	if session.RootChain == nil || session.ReceiveChain == nil || session.MyDHRatchet == nil {
		return "", errors.New("Session not initialized via handshake")
	}


	// Before we modify anything, we take a snapshot of the current session
	// state. If decryption fails, we must roll back to this exact state.
	snapshotPartnerKey := session.PartnerDHRatchet
	snapshotRootChain := session.RootChain.Duplicate()
	snapshotReceiveChain := session.ReceiveChain.Duplicate()
	snapshotCounterValue := session.ReceiveCounter

	// We need to gandle Skipped Messages from Previous Ratchet
	// The message's LastUpdate field tells us which message started the
	// sender's current ratchet. We must first process any skipped
	// messages before that point, using our current keys.
	if session.ReceiveCounter+1 < message.LastUpdate {
		precomputeSkippedMessageKeys(session, session.ReceiveCounter+1, message.LastUpdate)
	}

	// Then we check for a new DH Ratchet
	// We check if the message includes a new ratchet key and that it's
	// actually different from the one we already have.
	isNewDHRatchet := false
	if message.NextDHRatchet != nil && !areKeysIdentical(message.NextDHRatchet, session.PartnerDHRatchet) {
		// We only accept the new ratchet key if it's "on time",
		// i.e., associated with a message count at or after the LastUpdate.
		if session.ReceiveCounter <= message.LastUpdate {
			isNewDHRatchet = true
		}
	}

	// We'll need to reset our SendChain later if this is true
	needsSendChainReset := false
	if isNewDHRatchet {
		advanceReceiveRachet(session, message.NextDHRatchet)
		needsSendChainReset = true
	}

	// Next, we need tp advance to the Current Message Counter
	// Now, we fast-forward our (potentially new) receive chain to the
	// counter of the message we just got.
	if message.Counter > session.ReceiveCounter {
		advanceReceiveKeys(session, message.Counter)
	} else if message.Counter <= session.ReceiveCounter {
		// This is an out-of-order (or duplicate) message.
		// We must have its key in our cache.
		if _, keyExists := session.CachedReceiveKeys[message.Counter]; !keyExists {
			// We don't have the key. This is a critical error.
			// Roll back all state changes and reject the message.
			rollbackSessionStateAfterError(session, snapshotPartnerKey, snapshotRootChain,
				snapshotReceiveChain, snapshotCounterValue, message.Counter)
			return "", errors.New("Missing key for out-of-order message")
		}
	}

	// Decrypt
	// At this point, the key for message.Counter must be in the cache.
	messageKey := session.CachedReceiveKeys[message.Counter]
	if messageKey == nil {
		// This should be impossible if the logic above is correct, but check anyway.
		rollbackSessionStateAfterError(session, snapshotPartnerKey, snapshotRootChain,
			snapshotReceiveChain, snapshotCounterValue, message.Counter)
		return "", errors.New("Failed to retrieve message key from cache")
	}

	plaintext, err := messageKey.AuthenticatedDecrypt(message.Ciphertext, message.EncodeAdditionalData(), message.IV)
	if err != nil {
		// Decryption Failed! This is critical.
		// The message might be forged, or our state is corrupt.
		// We must roll back to the snapshot.
		rollbackSessionStateAfterError(session, snapshotPartnerKey, snapshotRootChain,
			snapshotReceiveChain, snapshotCounterValue, message.Counter)
		return "", err
	}

	// Lastly, we can clean up everything
	// Decryption was successful. We can now commit our state changes.

	// Securely wipe the one-time-use message key.
	messageKey.Zeroize()
	delete(session.CachedReceiveKeys, message.Counter)

	// If we performed a receive-ratchet, we must clear our SendChain.
	// This forces us to perform a send-ratchet on our next outgoing message.
	if needsSendChainReset && session.SendChain != nil {
		session.SendChain.Zeroize()
		session.SendChain = nil
	}

	// Finally, clean up the snapshots we created.
	snapshotRootChain.Zeroize()
	snapshotReceiveChain.Zeroize()

	// Return the decrypted message.
	return plaintext, nil
}