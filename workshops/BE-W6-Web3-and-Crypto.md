# Week 6 Mentor Session: Web3 & Crypto

## Session details

- **Track:** Backend AI Engineering
- **Mentor:** Alessandro Macagno
- **Portal date:** August 10, 2026, 1:00 PM
- **Portal duration:** 90 minutes
- **Recording:** [Alessandro Macagno: Web3 & Crypto](https://www.youtube.com/watch?v=ZE3eLTe4XTc)
- **Transcript used:** User-supplied automatic transcript. Its timestamps run to about 1:59, longer than the portal card's 90-minute duration. Speech-recognition errors are present; this note corrects terminology and checks technical explanations against primary documentation.

## What the mentor wanted learners to take away

The mentor framed the session as a practical orientation, not a trading class. The goal was to learn enough to judge when a blockchain might help a product or employer, understand the basic mechanics, verify claims using public chain data, and recognize common security traps. He explicitly said the session would not teach people to get rich, pick coins, or trade signals.

His central framing was **verifiability**. Decentralization is one way a system can be organized; the more useful question is what a participant can independently check. That verification has boundaries: wallet interfaces, RPC providers, bridges, and oracles can reintroduce reliance on particular operators or data sources.

## A working mental model

A blockchain is a shared state database that participating nodes update according to a protocol. Transactions are signed instructions; a consensus mechanism determines which valid updates become part of the shared history. Blocks group updates, and cryptographic links make changing past records detectable and costly under the network's rules. The precise security and confirmation model varies by chain. [Ethereum's technical introduction](https://ethereum.org/developers/docs/intro-to-ethereum/) · [Bitcoin: How it works](https://bitcoin.org/en/how-it-works)

The mentor called a blockchain an “expensive database” to emphasize the cost of replicated verification and execution. Treat this as a useful product-design analogy, not a complete technical definition: public chains also provide shared execution and consensus, and their costs and trust assumptions differ.

Bitcoin and Ethereum served as contrasting examples. Bitcoin uses proof of work; Ethereum now uses proof of stake. These are different ways of participating in consensus, with different operational and security trade-offs. Do not generalize one chain's rules to every blockchain. [Bitcoin: How it works](https://bitcoin.org/en/how-it-works) · [Ethereum: Proof of stake](https://ethereum.org/developers/docs/consensus-mechanisms/pos/)

## How a user action reaches the chain

1. A user chooses an address, network, amount, or contract action in an application.
2. A wallet prepares the transaction and asks the user to review and sign it with the account's private key.
3. The signed transaction is sent to a node, often through an RPC provider, and propagated to the network.
4. Validators or miners process transactions under that chain's consensus rules. If accepted, a block records the resulting state change.
5. A block explorer can display the transaction, block, addresses, contract, and status so a user can inspect what happened.

On Ethereum, a read-only query such as checking a balance does not change chain state and normally does not require a transaction fee. A write, such as transferring a token or calling a contract function, changes state and requires a signed transaction and gas. The transaction's sender pays the network fee; failed calls can still consume gas. [Ethereum: Interacting with smart contracts](https://ethereum.org/developers/docs/smart-contracts/interacting/) · [Ethereum: Transactions](https://ethereum.org/developers/docs/transactions/)

## Wallets, accounts, and keys

A wallet is software or hardware used to manage keys and interact with accounts; it is not a container that literally stores coins. On Ethereum, an externally owned account is controlled by keys, while a contract account is controlled by code. Public addresses can be shared to receive assets. Private keys and recovery phrases grant control and must stay secret. [Ethereum: Accounts](https://ethereum.org/developers/docs/accounts/) · [Bitcoin: How it works](https://bitcoin.org/en/how-it-works)

The recording sometimes describes crypto as anonymous. A safer description is **pseudonymous**: addresses do not inherently show a person's name, but transactions are public and can sometimes be connected to real identities through other information. Never share a seed phrase or private key with a person or “support agent”; anyone who gets it can take control of the account.

## Smart contracts and tokens

A smart contract is a program stored and executed on a blockchain. The name does not make it a legal contract or guarantee that its code is safe. Public contracts can be called by applications and other contracts; once a state-changing action is confirmed, reversing it may be difficult or impossible through ordinary user controls. [Ethereum: Introduction to smart contracts](https://ethereum.org/developers/docs/smart-contracts/)

Ethereum token standards define common contract interfaces so wallets and applications can interact with different tokens in a consistent way. The transcript says “EIP-20” or “ERC 20” in places; the standard is commonly called **ERC-20**, and its proposal is [EIP-20](https://eips.ethereum.org/EIPS/eip-20). ERC-721 is a standard interface for non-fungible tokens. A standard makes interfaces more predictable; it does not prove an individual token is legitimate, valuable, or safe. [Ethereum: Token standards](https://ethereum.org/developers/docs/standards/tokens/) · [ERC-721](https://ethereum.org/developers/docs/standards/tokens/erc-721)

The recording also introduces stablecoins and Layer 2 networks. A stablecoin is designed to track another asset, but its peg and redemption depend on its backing, issuer, mechanism, and market conditions. A Layer 2 system handles activity beyond the base chain and relies on some relationship with that base chain; bridges and cross-chain flows add their own assumptions and risks. These are concepts to investigate, not endorsements.

## What a blockchain cannot verify on its own

A blockchain cannot independently observe an off-chain event such as a weather reading, a bank balance, or who won an election. An oracle or other external service must provide the information. The chain can then record or execute against that input, but it cannot make the input true by itself. This creates an important trust boundary: check where the data came from and who can change it.

The same distinction applies to a polished dapp interface. A website can mislead users even when the contract is public. For important actions, verify the network, destination address, contract, requested permissions, and transaction details through an independent source where possible.

## Risks the session highlights

- **Key loss or theft:** a compromised recovery phrase can give an attacker control of the account.
- **Phishing and fake support:** urgent messages and requests to “verify” or reveal a seed phrase are common warning signs.
- **Irreversible actions:** sending to the wrong address or approving a malicious contract can be difficult to undo.
- **Contract and integration bugs:** open-source code and public visibility do not guarantee safety.
- **Oracle, bridge, RPC, and frontend dependence:** a dapp may depend on services that are more centralized than its chain.
- **Market and leverage risk:** the recording uses leveraged trading as an example, but explicitly disclaims trading instruction. Leverage can magnify losses; this note does not recommend trading or buying assets.

## A safe learning exercise from the session

The mentor's proposed homework was to deploy a simple contract on a test network and verify it with a block explorer. A test network is for practice; its tokens are not intended to represent mainnet value. Ethereum's current developer documentation identifies Sepolia for application and contract testing. [Ethereum: Networks and testnets](https://ethereum.org/developers/docs/networks/)

If you do this exercise, use a fresh test-only wallet, use only faucet-provided test tokens, and never reuse or disclose a personal wallet's recovery phrase. Record the network, contract address, transaction hash, and what the explorer shows. Do not switch to mainnet or use real funds just to complete the exercise.

## Why this matters to backend engineering

A Web3 application still has familiar application layers: a user interface, server-side logic, data retrieval, and monitoring. The difference is that some state changes are requested through a wallet and executed by contracts on a shared network. A backend engineer may work on an RPC integration, indexer, event processor, API, monitoring, or key-management boundary without writing a smart contract.

For each feature, ask what must be on-chain, what can remain in a conventional database, who signs state-changing transactions, which external services the app trusts, how failures are surfaced, and how users can independently verify the result. Use a public chain when shared, independently verifiable state is useful enough to justify the additional cost and complexity.

## Recording chapters

- [0:00 — Introduction, learning goals, and what the session will not cover](https://youtu.be/ZE3eLTe4XTc?t=0)
- [7:55 — Trust, verifiability, and the session roadmap](https://youtu.be/ZE3eLTe4XTc?t=475)
- [20:22 — Blockchain mechanics: blocks, keys, and consensus](https://youtu.be/ZE3eLTe4XTc?t=1222)
- [45:42 — Programmability, smart contracts, and standards](https://youtu.be/ZE3eLTe4XTc?t=2742)
- [1:00:22 — Practical applications and stablecoins](https://youtu.be/ZE3eLTe4XTc?t=3622)
- [1:17:43 — Risks, market examples, and career paths](https://youtu.be/ZE3eLTe4XTc?t=4663)
- [1:36:18 — Testnet exercise and contract verification](https://youtu.be/ZE3eLTe4XTc?t=5778)
- [1:56:34 — Closing principles: trust, verification, and system boundaries](https://youtu.be/ZE3eLTe4XTc?t=6994)

## Sources and limits

- [FlyRank recording](https://www.youtube.com/watch?v=ZE3eLTe4XTc) and the event description supplied for this note.
- A user-supplied automatic transcript was used to identify the session's actual emphasis, examples, and timestamps. The transcript is not reproduced here; its speech-recognition errors were corrected or omitted.
- [FlyRank mentor profile: Alessandro Macagno](https://internship.flyrank.ai/mentors/guest)
- Official technical references are linked in the relevant sections. They explain current Ethereum and Bitcoin mechanics; they do not imply that all chains work the same way.
