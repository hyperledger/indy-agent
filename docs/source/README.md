# Agent Protocol Specification

## Agent Types
Agents are a combination of functionality and storage that communicate via messages with other Agents. The functionality enables interacting with other Agents via business rules that may involve asking their controlling identity - e.g. a person. The primary storage is a wallet that holds the keys owned by the Agent, the DIDs of other Identities that have Agents, and the information necessary to manage Verifiable Credentials.

There are at least four types of Agents: Mobile and Institution Edge Agents, Cloud Agents, and Hubs, which are a variation on Cloud Agents. All four types have the ability to interact with the Ledger, a Wallet (data store) and can perform Identity-related actions - which is what makes it a bit tricky talking about Agent types. Since all of the types can perform all of the identity-related functions, what differentiates the types?

In this section we’ll try to define the canonical uses of the different Agent types, understanding that a specific instance of an Agent may blur the lines between these types. This picture from the Sovrin White Paper shows the relationships between Edge and Cloud agents.

![Agents](Agents.png)

### Mobile Edge Agents
Mobile Edge Agents directly interact with an owner Identity - a person - to manage interactions with other Edge Agents and their Identities. The classic Edge Agent is the mobile agent on a smartphone supporting the smartphone Owner. A Mobile Edge Agent is primarily a Holder/Prover - receiving VerCreds from other entities, and using those VerCreds to prove attributes of its Subject (Owner) Identity. However, there may be reasons for an Edge Agent Identity to want to issue VerCreds - such as to delegate authority to another Identity using VerCreds.

Mobile Edge Agents hold the keys and Link Secret for the Subject Identity, enabling it to establish Edge-to-Edge connections with other Identities. Put another way, Edge Agents hold application level data - the DIDs (and related keys) and Verifiable Credentials for it’s owners end-to-end relationships.  Mobile Edge Agents use Cloud Agents to handle transport between Edge Agents - not for Application level purposes.

But for two reasons, a Mobile Edge Agent could be the only Agent needed by an Identity:

* Since smartphones are not always online, a Cloud Agent can supplement the Mobile Edge Agent so that an Identity endpoint is always available.
* If the endpoint for an Identity is it’s Edge Agent internet address for all relationships, the single endpoint creates a public point of correlation. If the Edge Agent is accessed through an Agency’s Cloud Agent, the endpoint appears to be identical to all of the Agency’s other users.

### Institution Edge Agent
An Institution Edge Agent (IEA) is comparable to a Mobile Edge Agent but used to manage the Identity of an Organization in an Institution environment. IEA is not a mobile app, but an app running in an institutional environment - e.g. a private or public cloud, and extends the stereotypical Edge Agent by having a messaging API for configuring the business rules of the IEA.

As with any Edge Agent, it holds the private keys of the Organizational Identity. Where the typical Edge Agent goes to the user to ask how to respond to inputs from other agents, an IEA is configured to have access to a component that injects that “business knowledge” - potentially by connecting with the Edge Agent of user.  There are a number of suggestions for names for that component:
* Telegram Sam suggested “Static Agent” on the HL Indy call (June 7, 2018).
* BC Gov has talked about “Agent Owner” (as in the owner of the Agent) or Adaptor.

The proposed key aspects of Spot (see how I did that?) are that:
* It controls the Institution Edge Agent (a generic capability) with business specific configuration and control.
* It can be integrated with the existing Institution environment - reading from and potentially writing to the backend systems.
  * BC Gov is going to use it first as a Verifiable Credentials publisher to publish to TheOrgBook public registrations, licenses and permits.  No backend systems changes needed - just access to an event stream.
* It communicates with the IEA via encrypted messages, but will not itself have Indy Agent capabilities - Wallet, DIDs, etc. Mutual encryption will be configured (injected into) the Agent Owner and it’s IEA vs. dynamically created.
* It initiates actions to be performed by the IEA - “Create Schema”, “Create Credential Definition”, “Publish Credential”, etc.
* It registers message handlers for IEA to contact when it receives messages. These are optional and are used to add business rules into IEA’s flow. IEA should be configurable so as to do “the right thing” to reduce the complexity of the Agent Owner for simple scenarios.
* It configures the IEA through a Config API to do things like register handlers for messages, setting policies and defining default behaviours.

### Cloud Agents
One description of a Cloud Agent is an Agent that is used primarily for message transport, providing an Edge Agent with a persistent endpoint. This is shown in the canonical figure above from the Sovrin White Paper. Although a Cloud Agent could have many variations, the following assumes that model, with some variations documented at the end of this section.

#### Agencies and Agency Endpoints
A Cloud Agent is within an Agency - a multi-tenant, cloud-hosted Service. The endpoint for all Agents in the Agency is a high-availability Agency message queue based on a known protocol - most often HTTPS.  The endpoint knows only enough to decrypt the message it receives, and based on the decrypted message, what to do next with the message.  Most often, the next step will be to pass the payload of the decrypted message (which is likely also encrypted) to the Cloud Agent of the message Addressee. Within an Agency, each Cloud Agent is a configured instance of an Agent that communicates directly with the Edge Agent(s) of an Identity Owner. Since the Agency Endpoint decrypts an incoming message, it must have the private keys related to the public used to encrypt the message.

As such, there must be enough information implied or in the message passed to the endpoint to allow the Agency to decrypt the message.  Further, there must be enough information after the decryption for the Agency to be able to determine what Cloud Agent should handle the message further.

#### Cloud Agent Message Handling
The Cloud Agent must be able to respond to the payload of the message and be able to contact as necessary its associated Edge Agent(s). There are several classes of messages for the Cloud Agent to handle:

* Messages from other Agents to be forwarded to the Edge Agent. Such messages may be have to be queued for the Edge Agent to receive when they are online.
* Messages from the Edge Agent to the Agent of other Identities. Such messages need to be forwarded to the endpoint of the of the other Identity. The Cloud Agent may hold the necessary information for that action, or receive that with the message from the Edge Agent.
* Messages from the Edge Agent for administrative purposes. These are used for things like configuring the Cloud Agent, backups, restores and so on.

#### Cloud Agent Keys and Endpoints
The Cloud and Edge Agents must have keypairs so that two Agents can auth-crypt (encrypt and sign) messages to one another. Based on our core definition of the Cloud Agent being primarily for message transport, the Cloud Agent does not have keys for accessing the Application Layer content of messages - only the Edge Agents have those keys.

Mobile Edge Agents will by definition have a non-persistent endpoint and the Cloud Agent must have a way to message the Mobile Agent Agent, including queuing messages when the Edge Agent is offline. <<<How does this happen in the mobile world?  The Edge Agent maintains the connection with the Cloud Agent?>>>

#### Other Cloud Agent Functions
A Cloud Agent may have other functions beyond message transport. 

A key feature might be providing Wallet backup and restore functionality - holding an encrypted version of an Edge Agent’s wallet. The encryption and encryption key handling would be on the Agent side, but the encrypted data could be stored with the Cloud Agent. The encryption key handling would involve all of the DKMS mechanisms described in the [Evernym/DHS document](https://github.com/hyperledger/indy-sdk/blob/677a0439487a1b7ce64c2e62671ed3e0079cc11f/doc/design/005-dkms/DKMS%20Design%20and%20Architecture%20V3.md). So many details to be added…

#### Variations
In an Institution environment, a Cloud Agent is less important since the Edge Agent is likely a persistent end point using on-premise or Cloud hosting. It may still be useful to have a Cloud Agent to prevent correlation. Regardless, an IEA without a Cloud Agent should still look to the rest of the world like any other Agent, so it should have endpoint message handling like that of a Cloud Agent - e.g. expect to be sent [Base64](https://tools.ietf.org/html/rfc4648) encoded anon-encrypted messages via a transport with an id, message type, and appropriate message as the payload.

### Hubs
A Hub is much like a Cloud Agent, but rather than focusing only on messaging (transport) as defined above for a Cloud Agent, the Hub also stores and shares data (potentially including Verifiable Credentials), on behalf of its owner. All of the data held by the Hub is en/decrypted by the Edge Agent, so it is the data that moves between the Edge and Hub, and not keys.  The Hub storage can (kind of) be thought of as a remote version of a Wallet without the keys, but is intended to hold more than just the Verifiable Credentials of an Edge Agent wallet. The idea is that the user can push lots of, for example, app-related data to the Hub, and a Service would be granted permission by the Owner to directly access the data without having to go to the Edge Agent. For example, a Hub-centric music service would store the owner’s config information and playlists on the Hub, and the Service would fetch the data from the Hub on use instead of storing it on it’s own servers.

## Messaging Protocol
### Transport Payload - Message Packaging/Unpackaging
The process of handling messages should be consistent and independent of the transport mechanism of an agent implementation. The payload put onto the transport should be created in the following way:
* Anon-encrypt the base message structure
* [Base64](https://tools.ietf.org/html/rfc4648) encode the encrypted message

The point in the process after the transport mechanism has delivered the payload should also be consistent and follow these steps:

* [Base64](https://tools.ietf.org/html/rfc4648) decode the string
* Anon-decrypt the bytes

In order to anon encrypt/decrypt the payload, the endpoint (transport) mechanism MUST use a well known DID/VerKey associated with that endpoint called an Endpoint DID. The phrase "well known" conveys that the agents could either lookup the Endpoint DID on the ledger, or through some means share/configure the Endpoint DIDs between two agent implementations out of band. Either way, both agent endpoints need to "know" the Endpoint DID details in order to send messages back and forth. No matter what kind of transport is used, the Endpoint DID should be used to package/unpackage the payload through/from the transport by following the steps outlined above.

### Base/Core Message Structure
To maintain consistency of message handling, the following defines the structure of every message before it is packaged and sent over the transport layer or after it is received through the transport layer and unpackaged:
```json
{
  "id": "identifier/DID/nonce",
  "type": "URN message type",
  "message": {}
}
```
* The `id` attribute is required and needs to be either the DID of the sender that is a pairwise identifier in an established connection, a nonce used in establishing a connection, or another similar identifier used in a different custom message exchange.
* The `type` attribute is required and MUST be a recognized message type.
* The `message` attribute is required or optional depending upon the value of the type attribute and would contain the contents specified in the definition of the message type.
 
### Message Types
Message types MUST be in the form of a URN. For example, Sovrin implementations of Indy agents follow the structure of the URN as:

`urn:indy:sov:agent:message_type:<organization domain>/ <message family>/<major family version>.<minor family version/<message type>`

A change in the major family version indicates a breaking change, while the minor family version indicates a simple addition of information.

`urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/offer`

The following sections describe families of message types.

#### Connections (Relationships)
Connections allow establishing relationships between identities. The following are the specific message types and the order of the message exchange that is necessary to establish a connection/relationship:

##### Connection Offer:
The connection offer message is used to disclose the endpoint and the Endpoint DID information needed to exchange a connection request message. If the Endpoint DID and endpoint is already known or discoverable on the ledger, the connection offer is not necessary. If the Endpoint DID is not on the ledger, or not discoverable on the ledger, then the connection offer message is a way to communicate the necessary information to an agent in order to establish a connection/relationship. (We may need to make the endpoint attribute an object to convey transport information.) How the connection offer message is provided to the agent depends on the scenario in which the connection offer is used. You may use a QR code that relays the information, you may use a text message to relay the information, or a myriad other ways to relay the message. Eventually, the connection offer message needs to be anon-encrypted with the Endpoint DID, [Base64](https://tools.ietf.org/html/rfc4648) encoded as a string, and sent to the agent’s endpoint. Whatever mechanism is processing the QR code, text message, etc. needs to transform the message and send it to the endpoint. A mobile app, which would be a slim agent for this express purpose of relaying messages to a cloud/edge agent, might be a way to process a connection offer.
```JSON
{
 "id": "<offer_nonce>",
 "type": "urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_offer",
 "message": {
   "did": "<did>",
   "verkey": "<verkey>",
   "endpoint": "<endpoint>",
   "offer_nonce": "<offer_nonce>"
 }
}
```
* The `id` attribute of the base message is required and is a nonce used to correlate the connection request. The offer nonce is necessarily used when implementing an agency in order to route the connection request to the intended agent/wallet recipient.
* The `type` attribute of the base message is required and MUST be the value: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_offer`
* The `message` attribute of the base message is required, is not encrypted, and is an object containing the following attributes:
  * The `did` attribute is required and is the Endpoint DID.  that you can lookup on the ledger which also has an endpoint attribute
  * The `verkey` attribute is optional and is the verification key associated with the Endpoint DID. It is used if the Endpoint DID is not on the ledger or if the Endpoint DID on the ledger does not contain an endpoint attribute or [DID Document](https://w3c-ccg.github.io/did-spec/).
  * The `endpoint` attribute is optional and is the location used through the transport mechanism (i.e. URL if using http/https). It is used if the Endpoint DID is not on the ledger or if the Endpoint DID on the ledger does not contain an endpoint attribute or [DID Document](https://w3c-ccg.github.io/did-spec/).
  * The `offer_nonce` attribute is required and is a nonce used to correlate the connection request. The offer nonce is necessarily used when implementing an agency in order to route the connection request to the intended agent/wallet recipient.

##### Connection Request:
The connection request message is used to provide a DID to an agent in establishing a connection. The provided DID would usually be associated in a pairwise DID relationship in both participant’s wallet.
```JSON
{
 "id": "<offer_nonce>|<request_nonce>",
 "type": "urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_request",
 "message": {
   "did": "<did>",
   "nonce": "<request_nonce>",
   "endpoint_did": "<endpoint_did>",
   "endpoint": "<endpoint>"
 }
}
```
* The `id` attribute of the base message is required and is either the offer nonce used to correlate the connection request with a previous connection offer or the request nonce to uniquely identify the incoming connection request. The connection offer message and offer nonce are necessarily used when implementing an agency in order to route the connection request to the intended agent/wallet recipient. If an offer nonce exists as the id of a connection request message, the offer nonce is consumed when processing the connection request message. If a connection offer message was not initiated and a connection request message is the first message sent in the connection messages exchange, the value of the id attribute MUST be the request nonce.
* The `type` attribute of the base message is required and MUST be the value: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_request`
* The `message` attribute of the base message is required, is not encrypted, and is an object containing the following attributes:
  * The `did` attribute is required and is a DID created by the sender of the connection message.
  * The `request_nonce` attribute is required and is a nonce created by the sender of the connection request and used to correlate the connection request to a connection response.
  * The `endpoint_did` attribute is optional and is the Endpoint DID. It is used if the Endpoint DID is not on the ledger or if the Endpoint DID on the ledger does not contain an endpoint attribute or [DID Document](https://w3c-ccg.github.io/did-spec/).
  * The `endpoint` attribute is optional and is the location used through the transport mechanism (i.e. URL if using http/https). It is used if the Endpoint DID is not on the ledger or if the Endpoint DID on the ledger does not contain an endpoint attribute or [DID Document](https://w3c-ccg.github.io/did-spec/).

##### Connection Response:
The connection response message is used to respond to a connection request message and provide a DID to the sender of the connection request message to be used as a pairwise DID in an established connection/relationship.
```JSON
{
 "id": "<request_nonce>",
 "type": "urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_response",
 "message": "aGVsbG8K..." 
}
```
* The `id` attribute of the base message is required and is the request nonce sent in the connection request message and is used to correlate the connection response message to a specific connection request. The request nonce is consumed when the connection response message is processed.
* The `type` attribute of the base message is required and MUST be the value: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_response`
* The `message` attribute of the base message is required, is anon-encrypted with the verification key associated with the DID sent in the connection request, and [Base64](https://tools.ietf.org/html/rfc4648) encoded. The message is an object with the following attributes:
```JSON
{
   "did": "<did>",
   "verkey": "<verkey>",
   "request_nonce": "<request_nonc>"
}
```
  * The `did` attribute is required and is a DID created by the sender of the connection response message. This DID is usually used in creating a pairwise DID with the DID sent in the connection request message.
  * The `verkey` attribute is required and is the verification key of the DID in the did attribute.
  * The `request_nonce` attribute is required and is a nonce used to correlate the connection response message to a specific connection request message.

##### Connection Acknowledgement:
The connection acknowledgement message is used to confirm that a connection/relationship has been established. The connection acknowledgement message also contains an auth-encrypted message now possible between pairwise DIDs established on each side of the connection. This auth-encrypted pattern is important as a foundation for other message types to be designed requiring privacy and protected data.
```JSON
{
 "id": "<did>",
 "type": "urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_acknowledgement",
 "message": "aGVsbG8K..." 
}
```
* The `id` attribute of the base message is required and is the DID of the sender of the connection acknowledgement message in the pairwise DID established connection/relationship.
* The `type` attribute of the base message MUST be the value: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/connection_acknowledgement`
* The `message` attribute of the base message is required, is auth-encrypted, and [Base64](https://tools.ietf.org/html/rfc4648) encoded. The message is the simple string value `"success"`.

#### Credentials
Credentials are verifiable attestations or assertions that one identity is making about another identity. The specific message types and the order of the message type exchange that is necessary to issue and receive a credential are:

##### Credential Offer
Message Type: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/credential_offer`

##### Credential Request
Message Type: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/credential_request`

##### Credential
Message Type: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/credential`

#### Proofs
Proofs are verifiable assertions about credential data and conditions of the credential data. The specific message types and the order of the message type exchange that is necessary to receive a proof are:

##### Proof Request
Message Type: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/proof_request`

##### Proof
Message Type: `urn:indy:sov:agent:message_type:sovrin.org/connection/1.0/proof`
