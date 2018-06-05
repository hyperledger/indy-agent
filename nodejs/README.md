# node.js implementation of the indy-agent
#### Note: The indy-agent is a work in progress and is not ready for use.

## Quick start guide

See these [quick start instructions](quick-start-guide.md) for running this Agent implementation.

## Basic Design Overview

The agent is a simple http server that can receive messages [POST](https://en.wikipedia.org/wiki/POST_(HTTP))ed to the /indy endpoint.  Those messages are stored for the user to make decisions on later through the UI. The UI is used to:

* Create new relationships
* Decide to accept new relationship requests
* Send and manage Credentials
* Make and request proofs

## Notes
* The Issuer page could be simplified.  Why not let the only action be issue credential and have them pick a schema. If the cred def doesn't exist, just create it.
* They will need the ability to create schemas. That could be a separate tab. Schema Explorer.