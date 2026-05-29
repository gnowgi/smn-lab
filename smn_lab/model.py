# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 G. Nagarjuna and Durgaprasad Karnam
"""MJCF model builders for the SMN embodied bench.

P0 body: a single Coordinated Action Zone (CAZ) realized as a yaw 'head' driven
by a pull-only antagonist actuator pair (the two Sensation Modulators of the
zone), carrying one rangefinder 'whisker' (a single-interface transducer, S),
inside a walled arena. A movable object delivers *exafference* -- a world-caused
sensory change the agent did not produce.

The whisker site is oriented so its rangefinder ray (+Z of the site frame)
points along the head's forward (+X) direction; as the head yaws, the whisker
sweeps the scene.
"""


def build_p0_xml(arena_half: float = 1.2, wall_h: float = 0.15,
                 head_z: float = 0.15, cmax: float = 1.5) -> str:
    """Return the MJCF for the P0 single-CAZ + whisker arena."""
    return f"""
<mujoco model="smn_p0_caz_whisker">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.005" gravity="0 0 -9.81" integrator="RK4"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3"/>
  </visual>

  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <geom name="floor" type="plane" size="3 3 0.1" rgba="0.92 0.92 0.92 1"/>

    <!-- arena walls (sealed box) -->
    <geom name="wall_n" type="box" pos="0 {arena_half} {head_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_s" type="box" pos="0 {-arena_half} {head_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_e" type="box" pos="{arena_half} 0 {head_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_w" type="box" pos="{-arena_half} 0 {head_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.6 0.6 0.6 1"/>

    <!-- agent: a single CAZ = head that yaws about z -->
    <body name="head" pos="0 0 {head_z}">
      <joint name="yaw" type="hinge" axis="0 0 1" limited="false" damping="0.05"/>
      <geom name="head_geom" type="box" size="0.08 0.05 0.05" rgba="0.2 0.4 0.9 1" mass="0.2"/>
      <!-- whisker: site +Z -> head +X (forward); placed just ahead of the head -->
      <site name="whisker" pos="0.12 0 0" euler="0 90 0" size="0.005" rgba="1 0.6 0 1"/>
    </body>

    <!-- movable object: slides along x; parked far during learning, brought in for exafference -->
    <body name="obj" pos="0 0 {head_z}">
      <joint name="obj_slide" type="slide" axis="1 0 0" limited="false"/>
      <geom name="obj_geom" type="cylinder" size="0.06 {wall_h}" rgba="0.9 0.3 0.2 1" mass="1" contype="0" conaffinity="0"/>
    </body>
  </worldbody>

  <actuator>
    <!-- pull-only antagonist pair (the zone's two Sensation Modulators) -->
    <motor name="m_right" joint="yaw" gear="1"  ctrlrange="0 {cmax}"/>
    <motor name="m_left"  joint="yaw" gear="-1" ctrlrange="0 {cmax}"/>
  </actuator>

  <sensor>
    <rangefinder name="whisker_range" site="whisker"/>
    <jointpos name="yaw_pos" joint="yaw"/>
    <jointvel name="yaw_vel" joint="yaw"/>
  </sensor>
</mujoco>
"""
