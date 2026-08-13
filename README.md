<p align="center">
  <img src="assets/brainrash-logo.png" width="120" alt="Pale Blue Dot, photographed by Voyager 1 from 6 billion km away">
</p>

<h1 align="center">BrainRash</h1>

<p align="center">
  <i>Sharing insights and experiences in tech, maths, science, and whatever else turns out to be interesting.</i>
</p>

<p align="center">
  <a href="https://brainrash.substack.com/"><img src="https://img.shields.io/badge/Substack-Subscribe-FF6719?style=for-the-badge&logo=substack&logoColor=white" alt="Subscribe on Substack"></a>
</p>

---

## About BrainRash

This repo holds the code behind [BrainRash](https://brainrash.substack.com/), a running record of things I've learned and whatever else stuck.

For more information on my blog, check out the [pilot post](https://brainrash.substack.com/p/pilot).

## How this is organised

Posts follow the pattern `ABCDE-###`: a 5-letter code for the topic, followed by a post number within that thread. `sut30-003` is the third post in the sut30 thread, for example. Every thread starts with a `000` post, its index page, explaining what the thread covers and linking to every post in it as they go up.

This repo mirrors that pattern. Each thread gets a lowercase folder under `threads/`, and each post gets its own numbered subfolder inside it, holding whatever code that post needed.

| Thread | About |
|--------|-------|
| [`sut30/`](./threads/sut30) | Working through the Sutskever 30 list. Implementing one foundational ML/CS paper at a time. |
| [`poker/`](./threads/poker) | Building a Texas Hold'em poker AI from scratch: CFR, game theory, and the GTO-to-exploit pipeline, worked through and written up as I go. |

Each thread's README carries a grid of its posts published so far, which rewrites itself automatically on every push, so it's never stale.

## Follow along

New posts go up on [BrainRash](https://brainrash.substack.com/) first. Subscribe there if you want them before the code catches up.