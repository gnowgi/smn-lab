# NetLogo — feasibility report

This page records what was found when the question *"could `smn-lab` be planted
in the NetLogo house — to reach a much larger agent-based modeling
community?"* was investigated. **No integration path is committed.** The page
preserves the landscape so a future maintainer (or you, returning to this
question) can decide without re-doing the research.

## Why the question

NetLogo, developed at the [Center for Connected Learning](https://ccl.northwestern.edu/netlogo/)
(CCL, Northwestern), is the dominant teaching-and-research platform for
agent-based modeling: large library of community models, well-known among
educators, computational social scientists, and ecologists. The natural
question for any embodied-agent bench is whether it can carry its argument into
that community — even at the cost of wiring MuJoCo to NetLogo's runtime
rather than reusing the NetLogo codebase.

What follows is what would have to be true (or be built) for that to work, and
what is honestly in it for both communities once it is.

## The four realistic paths

| Path | Key enabler | Current state | Strength | Cost |
|---|---|---|---|---|
| **A. NetLogo desktop extension wrapping MuJoCo** | [`mujoco-java`](https://github.com/CommonWealthRobotics/mujoco-java) — JNI binding on Maven Central as `com.neuronrobotics:mujoco-java:3.1.3-pre.17` (March 2025) | Pre-release but maintained; Linux / macOS / Windows; small project (~15★, ongoing PRs) | Deepest integration. NetLogo is the host; reaches the community in its idiom. Reuses the MuJoCo binary, no port. | Major engineering — the SMN control layer is re-expressed in Scala / Java, or shelled out via the `py` extension (which defeats the point). Cross-platform JNI loading. Pre-release dependency. |
| **B. Python-driven NetLogo from outside** | [`pyNetLogo`](https://pypi.org/project/pynetlogo/) (Quaquel, v0.3.2 Feb 2024) / [`NL4Py`](https://github.com/chathika/NL4Py) (Gunaratne et al., py4j-based) | Mature; production-used for headless sweeps | Smallest commitment. `smn-lab` core stays in Python; the `.nlogo` file is a viewer + parameter UI driven from outside. | NetLogo is "demoted" to a front-end. The community may read it as "Python with NetLogo bolted on" — which it is. |
| **C. NetLogo Web + Python+MuJoCo backend over HTTP/WebSocket** | NetLogo Web's bundled HTTP-Req extension + a `smn-lab` Python server | Pieces all exist; no precedent for this exact wiring | Highest visibility — one URL, no install. Aligns with [the NLW physics-extension forum thread](https://forum.netlogo.org/t/physics-extension-for-nlw/503). | Latency-bound (10–50 ms round-trips); hosting + reliability burden; not real-time enough for tight sensorimotor loops. |
| **D. NetLogo Web fork + MuJoCo WASM bundled in-page** | [Official `mujoco/wasm`](https://github.com/google-deepmind/mujoco/tree/main/wasm) (Google DeepMind) + a forked Galapagos with a custom Tortoise extension | WASM build proven by demos ([zalo/mujoco_wasm](https://zalo.github.io/mujoco_wasm/), [RoboPianist](https://kzakka.com/robopianist/)); Galapagos fork is uncharted | Self-contained browser app; zero server; most impressive demo. | The largest bet. NLW extensions must be compiled into Galapagos at build time; we'd carry and maintain a fork. |

## Technical caveats that bind every in-NetLogo path

- The NetLogo engine is **single-threaded** by design. Every primitive blocks
  the tick. Acceptable for embodied real-time simulation (MuJoCo's `mjStep` is
  fast); painful for big batch sweeps from inside NetLogo (do those from
  Python).
- Native code called from `monitor` reporters crashes the JVM
  ([NetLogo issue #2033](https://github.com/NetLogo/NetLogo/issues/2033)).
  Workaround: only call MuJoCo (or any JNI primitive) from *commands*, never
  from a `monitor` widget.
- **NetLogo Web has no runtime extension loading.** Tortoise extensions must
  be compiled into Galapagos at build time (a JS implementation + a JSON
  definition file, both checked into the Galapagos source). Anything that
  needs custom primitives in the browser requires forking Galapagos and
  shipping the fork — there is no `.zip` extension drop the way the desktop
  has.
- pyNetLogo / NL4Py invert the host relationship: Python is the driver, NetLogo
  is the controlled process. Useful for headless sweeps and as a front-end
  driver, but it means NetLogo is not "in charge" of the simulation step.

## The honest version of "visibility"

The community-size argument needs unbundling. Two readings of the audience
matter:

**The NetLogo community asks for *some* physics — but not at MuJoCo's level.**
There is an active [forum thread requesting a physics extension for NetLogo
Web](https://forum.netlogo.org/t/physics-extension-for-nlw/503), and an
existing official [Physics Extension](https://github.com/NetLogo/Physics-Extension)
on the desktop built on Dyn4J. Both are at the **Box2D / 2D-collision** level:
flocking with collisions, predator-prey games, simple force fields. There is
no community demand for MuJoCo-grade morphodynamics — joint torques, contact
geometry, muscle actuation, energy economics. Bringing MuJoCo to NetLogo would
overshoot what the community currently asks for.

**The embodied-cognition / 4E community already chose its tools, *outside*
ABM.** Webots, MuJoCo, Isaac Sim are the established simulators precisely
because their fidelity is what makes embodied cognition empirically tractable.
Bolting MuJoCo onto NetLogo will not draw that community in; if anything, the
ABM idiom (turtles, patches, ticks) reads to them as the abstraction they
*chose* to escape.

The genuine cross-pollination niche is **educational**. Biology, cognitive
science, and CS instructors and students who are NetLogo-literate would meet
embodied SMN agents in their own idiom — the basal-coupling story and the
map-guided foraging story landing as `.nlogo` files they can open and play
with. There is also a smaller research bridge for ecological /
biomechanical ABM work where physics-grounded behavior matters but the
modelers are NetLogo-native (population biology, behavioural ecology).

That is a real audience, narrower than "the whole NetLogo community" — and
clear-eyed about it from the start is the right way to scope any future
build.

## Sources

- [NetLogo Extensions API Wiki](https://github.com/NetLogo/NetLogo/wiki/Extensions-API)
- [NetLogo 7 Extensions Guide](https://docs.netlogo.org/extensions.html)
- [Official Python extension (`py`)](https://docs.netlogo.org/py.html) · [repo](https://github.com/NetLogo/Python-Extension)
- [`pyNetLogo` on PyPI](https://pypi.org/project/pynetlogo/) — Python-drives-NetLogo bridge
- [`NL4Py` repo](https://github.com/chathika/NL4Py) · [arXiv 1808.03292](https://arxiv.org/abs/1808.03292)
- [`mujoco-java` on GitHub](https://github.com/CommonWealthRobotics/mujoco-java) — JNI binding on Maven Central
- [Official MuJoCo WASM build](https://github.com/google-deepmind/mujoco/tree/main/wasm) · live demo: [zalo.github.io/mujoco_wasm](https://zalo.github.io/mujoco_wasm/)
- [Galapagos (NetLogo Web)](https://github.com/NetLogo/Galapagos) · [Tortoise compiler](https://github.com/NetLogo/Tortoise) · [Experimental extensions wiki](https://github.com/NetLogo/Tortoise/wiki/Experimental:-Extensions)
- [NetLogo official Physics Extension (Dyn4J)](https://github.com/NetLogo/Physics-Extension)
- [Forum: Physics Extension for NetLogo Web](https://forum.netlogo.org/t/physics-extension-for-nlw/503)
- [NetLogo issue #2033 — native code crash in monitor reporters](https://github.com/NetLogo/NetLogo/issues/2033)

## Status

No integration path is committed. This page is a reference. If a future
maintainer decides to pursue one of A–D, the natural first move is a small
**scout** of Path B (`pyNetLogo`-driven NetLogo using one of the existing
basal-coupling or map-guided-foraging experiments) — because it commits the
least, surfaces the integration overheads honestly, and produces a real
`.nlogo` artifact that can be shown to one or two NetLogo channels before any
deeper investment.
