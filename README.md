Indy Agents
===========

Archiving Notice
----------------

**This repo has been archived (marked read only). There was GPL code removed; as such,
the contents of the repo are not usable as Apache 2.0 source even if copied out.**

Migration Notice
----------------

**The work of creating interoperable Agents has moved to the Hyperledger Aries Project.** Much of the code and
information in this repository remains relevant as a reference point; however, this information is not as actively kept
up to date and **may be incorrect**. For the up-to-date counterparts of the components in this repository, refer to the
list below.

#### Superseding Projects
- Docs and Protocol: [Indy HIPE][1] for Indy specific documentation, [Aries RFCs][2] for everything else.
- Python Reference Agent: [Aries Cloud Agent Python][3]
- Agent Test Suite: [Aries Protocol Test Suite][4]
- Node.js Agent: No codebase yet exists that directly supersedes this project. However, discussion around creating a
	Node.js Agent Framework are being held in the Aries Community. Direct questions about these efforts to the
	[Hyperledger Rocket.Chat Aries channel][5].

[1]: https://github.com/hyperledger/indy-hipe
[2]: https://github.com/hyperledger/aries-rfcs
[3]: https://github.com/hyperledger/aries-cloudagent-python
[4]: https://github.com/hyperledger/aries-protocol-test-suite
[5]: https://chat.hyperledger.org/channel/aries

#### Other questions?
Direct any other questions you may have about this repository to the [Aries channel][5].

Agents
------

Agents come in all varieties. Some are simple and static; these
might be appropriate for IoT use cases that are hard-wired for
a single connection. Others are complex and cloud-based, suitable
for enterprise use. Still others run on mobile devices for
individual users. For more information about general agent theory
or about agent categories, see the [Agents Explainer HIPE](
https://github.com/hyperledger/indy-hipe/blob/4696f162/text/0002-agents/README.md).

This repo contains a handful of reference agents. To run them,
you must have a build of libindy plus a running ledger.  If you
are just trying them out, we recommend [running a ledger locally
using docker](https://github.com/hyperledger/indy-sdk/blob/master/docs/build-guides/ubuntu-build.md).
See the README in each implementation directory for more
details.

The repo also has some useful tools for agent developers--especially
a test suite that can exercise agent interoperability.

## Known Agent Implementations

The following agents are known to the general community. If you
would like to list your agent here, please submit a pull request.

|Name|Source|Use Cases|Interop Results from Test Suite|More Info|
|----|------|---------|-------------------------------|---------|
|python ref agent|community / Sovrin Foundation (see github contributors)|cloud (web-based)|not yet published on the web, but 100% passed in Feb 2019|see [python/README.md](python/README.md) in this repo|
|node.js ref agent|community / BYU (see github contributors)|cloud (web-based)|not yet tested|see [nodejs/README.md](nodejs/README.md) in this repo|
|Sovrin Connector|Sovrin Foundation|mobile app (assumes cloud support)|not yet tested|[github.com/ sovrin-foundation/ connector-app](https://github.com/sovrin-foundation/connector-app)|
|IndyCat|Government of British Columbia|Cloud for institutions (besides agent, includes drive to enable injection of business rules in messaging protocols)|100% passed in Feb 2019|[https://github.com/bcgov/indy-catalyst/](https://github.com/bcgov/indy-catalyst/tree/master/agent)|
|AgentFramework|AgentFramework|.NET framework for building agents of all types|Samples in the repository 100% passed in Feb 2019|[agent-framework](https://github.com/streetcred-id/agent-framework)|
|Streetcred|Streetcred|Commercial mobile and web app built using AgentFramework|Samples in AgentFramework 100% passed in Feb 2019|[streetcred.id](https://streetcred.id)|
|Mattr|Mattr|Commercial mobile and web app built using AgentFramework|Samples in AgentFramework 100% passed in Feb 2019|[mattr.global](https://mattr.global)|
|Project Osma|Mattr|Open source mobile app built using AgentFramework|not yet tested|[project](https://github.com/mattrglobal/osma)|
|Verity|Evernym|commercial enterprise agent, focused on credential issuance and proving for login and onboarding|not yet tested|[evernym.com](https://evernym.com)|
|Connect.Me|Evernym|commercial mobile agent for individuals (free but requires SaaS subscription for supporting cloud agent)|not yet tested|Android or iOS App Store|
|Pi Agent | Evernym | Simple cli agent for connecting and sending basic messages. Useful in IOT (Raspberry Pi) applications. | 100% passed in April 2019 | [https://github.com/evernym/connectathon-agent](https://github.com/evernym/connectathon-agent) |
|StudyBits University Agent | Quintor | Cloud agent for universities for use in student exchange | Definitely would not pass | [GitHub](https://github.com/Quintor/StudyBits) [Project](https://www.bcined.com/studybits.html) |
|StudyBits (Android) Wallet | Quintor | Mobile wallet for use in student exchange | Definitely would not pass | [GitHub](https://github.com/Quintor/StudyBitsWallet) |

## Related Topics

If you are interested in developing indy-sdk,
please visit the [indy-sdk repository](https://github.com/hyperledger/indy-sdk/)
and follow the Getting Started Guide there.


