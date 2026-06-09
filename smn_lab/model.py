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


def build_p0v_xml(arena_half: float = 1.6, wall_h: float = 0.30,
                  head_z: float = 0.15, cmax: float = 1.5,
                  fov_deg: float = 90.0) -> str:
    """P0-visual: the P0 single-CAZ head with a forward-facing camera.

    The transducer changes (whisker → camera); the architecture does not. The
    camera sits at the head's pivot so rotation is about the optical center —
    keeping the analytical flow predictor (uniform horizontal flow from yaw
    rate) exact under a static-world assumption. The arena has a checker-
    textured floor and coloured walls so the SAD block-matcher has signal; the
    cylindrical exafference object is the same one P0 uses, slid in front of
    the agent during the exafference window.
    """
    return f"""
<mujoco model="smn_p0_visual">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.005" gravity="0 0 -9.81" integrator="RK4"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.8 0.8 0.8" ambient="0.4 0.4 0.4"/>
  </visual>

  <asset>
    <texture name="floor_tex" type="2d" builtin="checker"
             rgb1="0.85 0.85 0.85" rgb2="0.55 0.55 0.55" width="200" height="200"/>
    <material name="floor_mat" texture="floor_tex" texrepeat="6 6" reflectance="0.0"/>
  </asset>

  <worldbody>
    <light pos="0 0 3" dir="0 0 -1" diffuse="0.9 0.9 0.9"/>
    <geom name="floor" type="plane" size="3 3 0.1" material="floor_mat"/>

    <!-- arena walls in distinct colours, taller than P0 so they fill more of the camera view -->
    <geom name="wall_n" type="box" pos="0 {arena_half} {wall_h}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.85 0.40 0.30 1"/>
    <geom name="wall_s" type="box" pos="0 {-arena_half} {wall_h}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.30 0.55 0.85 1"/>
    <geom name="wall_e" type="box" pos="{arena_half} 0 {wall_h}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.35 0.75 0.40 1"/>
    <geom name="wall_w" type="box" pos="{-arena_half} 0 {wall_h}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.85 0.75 0.30 1"/>

    <!-- agent: the same single-CAZ head as P0, with the camera at its pivot -->
    <body name="head" pos="0 0 {head_z}">
      <joint name="yaw" type="hinge" axis="0 0 1" limited="false" damping="0.05"/>
      <geom name="head_geom" type="box" size="0.08 0.05 0.05" rgba="0.2 0.4 0.9 1" mass="0.2"/>
      <!-- camera at the pivot (rotation about its own optical center); looks along head +X.
           xyaxes = (camera +x in body frame, camera +y in body frame) → camera -z = head +x. -->
      <camera name="eye" pos="0 0 0.04" xyaxes="0 -1 0 0 0 1" fovy="{fov_deg}"/>
    </body>

    <!-- exafference object: slides along x; parked far during calibration, brought in for exafference. -->
    <body name="obj" pos="0 0 {head_z}">
      <joint name="obj_slide" type="slide" axis="1 0 0" limited="false"/>
      <geom name="obj_geom" type="cylinder" size="0.16 {wall_h}" rgba="0.95 0.25 0.20 1" contype="0" conaffinity="0" mass="1"/>
    </body>
  </worldbody>

  <actuator>
    <motor name="m_right" joint="yaw" gear="1"  ctrlrange="0 {cmax}"/>
    <motor name="m_left"  joint="yaw" gear="-1" ctrlrange="0 {cmax}"/>
  </actuator>

  <sensor>
    <jointpos name="yaw_pos" joint="yaw"/>
    <jointvel name="yaw_vel" joint="yaw"/>
  </sensor>
</mujoco>
"""


def build_p1v_xml(arena_half: float = 1.6, wall_h: float = 0.30,
                  head_z: float = 0.15, cmax: float = 1.5,
                  eye_yaw_range_deg: float = 25.0,
                  fov_deg: float = 90.0) -> str:
    """P1-visual: P0-visual + a multi-CAZ eye nested in the head.

    The eye is its own small body inside the head with its own yaw hinge and
    its own pull-only opponent pair (`m_eye_right`, `m_eye_left`). The camera
    is mounted on the eye, so the camera's total yaw in world is
    ``head_yaw + eye_yaw``. The forward model accordingly predicts from the
    sum -- whichever CAZ pair (body or eye) produced the motion is the one
    the modulator predicts away.

    This is the bench's minimal multi-CAZ-eye geometry: two CAZ pairs in
    total -- one for the head, one for the eye -- both about z. Pitch and a
    richer per-region CAZ ensemble come in later experiments.
    """
    return f"""
<mujoco model="smn_p1_visual">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.005" gravity="0 0 -9.81" integrator="RK4"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.8 0.8 0.8" ambient="0.4 0.4 0.4"/>
  </visual>

  <asset>
    <texture name="floor_tex" type="2d" builtin="checker"
             rgb1="0.85 0.85 0.85" rgb2="0.55 0.55 0.55" width="200" height="200"/>
    <material name="floor_mat" texture="floor_tex" texrepeat="6 6" reflectance="0.0"/>
  </asset>

  <worldbody>
    <light pos="0 0 3" dir="0 0 -1" diffuse="0.9 0.9 0.9"/>
    <geom name="floor" type="plane" size="3 3 0.1" material="floor_mat"/>

    <geom name="wall_n" type="box" pos="0 {arena_half} {wall_h}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.85 0.40 0.30 1"/>
    <geom name="wall_s" type="box" pos="0 {-arena_half} {wall_h}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.30 0.55 0.85 1"/>
    <geom name="wall_e" type="box" pos="{arena_half} 0 {wall_h}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.35 0.75 0.40 1"/>
    <geom name="wall_w" type="box" pos="{-arena_half} 0 {wall_h}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.85 0.75 0.30 1"/>

    <body name="head" pos="0 0 {head_z}">
      <joint name="head_yaw" type="hinge" axis="0 0 1" limited="false" damping="0.05"/>
      <geom name="head_geom" type="box" size="0.08 0.05 0.05" rgba="0.2 0.4 0.9 1" mass="0.2"/>
      <body name="eye" pos="0 0 0.04">
        <joint name="eye_yaw" type="hinge" axis="0 0 1" range="{-eye_yaw_range_deg} {eye_yaw_range_deg}" damping="0.0008"/>
        <geom name="eye_geom" type="sphere" size="0.018" rgba="0.95 0.95 0.20 1" mass="0.005"/>
        <camera name="eye" pos="0 0 0" xyaxes="0 -1 0 0 0 1" fovy="{fov_deg}"/>
      </body>
    </body>

    <body name="obj" pos="0 0 {head_z}">
      <joint name="obj_slide" type="slide" axis="1 0 0" limited="false"/>
      <geom name="obj_geom" type="cylinder" size="0.16 {wall_h}" rgba="0.95 0.25 0.20 1" contype="0" conaffinity="0" mass="1"/>
    </body>
  </worldbody>

  <actuator>
    <motor name="m_head_right" joint="head_yaw" gear="1"     ctrlrange="0 {cmax}"/>
    <motor name="m_head_left"  joint="head_yaw" gear="-1"    ctrlrange="0 {cmax}"/>
    <motor name="m_eye_right"  joint="eye_yaw"  gear="0.04"  ctrlrange="0 {cmax}"/>
    <motor name="m_eye_left"   joint="eye_yaw"  gear="-0.04" ctrlrange="0 {cmax}"/>
  </actuator>

  <sensor>
    <jointpos name="head_yaw_pos" joint="head_yaw"/>
    <jointvel name="head_yaw_vel" joint="head_yaw"/>
    <jointpos name="eye_yaw_pos"  joint="eye_yaw"/>
    <jointvel name="eye_yaw_vel"  joint="eye_yaw"/>
  </sensor>
</mujoco>
"""


def build_p1_xml(arena_half: float = 1.4, wall_h: float = 0.15,
                 body_z: float = 0.12, cmax: float = 2.5,
                 whisker_angles_deg=(-60, -30, 0, 30, 60)) -> str:
    """MJCF for the P1 multi-CAZ mobile agent (a 'toy mouse').

    A planar agent (slide-x, slide-y, yaw) carries a fan of rangefinder whiskers
    (single-interface transducers, S). Steering is a Coordinated Action Zone
    driven by a pull-only antagonist pair; forward locomotion is applied as a
    body-frame thrust (the BAP drive, set by the controller). Walls plus two
    interior objects give the agent a world to map.
    """
    import math
    sites, sensors = [], []
    for i, deg in enumerate(whisker_angles_deg):
        a = math.radians(deg)
        sites.append(
            f'      <site name="whisker_{i}" pos="0.12 0 0" '
            f'zaxis="{math.cos(a):.5f} {math.sin(a):.5f} 0" size="0.004" rgba="1 0.6 0 1"/>')
        sensors.append(f'    <rangefinder name="whisker_{i}" site="whisker_{i}"/>')
    sites = "\n".join(sites)
    sensors = "\n".join(sensors)
    return f"""
<mujoco model="smn_p1_mouse">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.005" gravity="0 0 -9.81" integrator="RK4"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3"/>
  </visual>

  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <geom name="floor" type="plane" size="3 3 0.1" rgba="0.92 0.92 0.92 1"/>

    <geom name="wall_n" type="box" pos="0 {arena_half} {body_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_s" type="box" pos="0 {-arena_half} {body_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_e" type="box" pos="{arena_half} 0 {body_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_w" type="box" pos="{-arena_half} 0 {body_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.6 0.6 0.6 1"/>

    <!-- interior objects to map -->
    <geom name="obj_cyl" type="cylinder" pos="0.55 0.45 {body_z}" size="0.12 {wall_h}" rgba="0.9 0.3 0.2 1"/>
    <geom name="obj_box" type="box" pos="-0.6 -0.35 {body_z}" size="0.12 0.18 {wall_h}" rgba="0.2 0.7 0.3 1"/>

    <!-- agent: planar mobile 'mouse' with a steering CAZ and a whisker fan -->
    <body name="mouse" pos="0 0 {body_z}">
      <joint name="slide_x" type="slide" axis="1 0 0" damping="2.0"/>
      <joint name="slide_y" type="slide" axis="0 1 0" damping="2.0"/>
      <joint name="yaw" type="hinge" axis="0 0 1" damping="0.15"/>
      <geom name="mouse_body" type="box" size="0.09 0.06 0.05" rgba="0.2 0.4 0.9 1" mass="0.4"/>
{sites}
    </body>
  </worldbody>

  <actuator>
    <motor name="m_yaw_right" joint="yaw" gear="1"  ctrlrange="0 {cmax}"/>
    <motor name="m_yaw_left"  joint="yaw" gear="-1" ctrlrange="0 {cmax}"/>
  </actuator>

  <sensor>
{sensors}
    <jointpos name="x_pos" joint="slide_x"/>
    <jointpos name="y_pos" joint="slide_y"/>
    <jointpos name="yaw_pos" joint="yaw"/>
    <jointvel name="yaw_vel" joint="yaw"/>
  </sensor>
</mujoco>
"""


def build_p3_xml(obj_radius: float, obj_rgba: str, obj_pos,
                 arena_half: float = 1.4, wall_h: float = 0.15,
                 body_z: float = 0.12, cmax: float = 2.5,
                 whisker_angles_deg=(-60, -30, 0, 30, 60),
                 cosmetic: bool = False) -> str:
    """MJCF for the P3 cross-modal discrimination scene.

    The same planar 'mouse' as P1/P2 (slide-x, slide-y, yaw, a whisker fan, and
    an IMU for proprioceptive self-localization), facing a single cylindrical
    object placed ahead of it. The object carries two of the three modality bits
    *geometrically* -- its **radius** (the tactile bit: a bigger object subtends
    more whiskers at a fixed gap) and its **luminance** via ``obj_rgba`` (the
    visual bit) -- while the third, taste, is an analytic chemical field sampled
    in the experiment. One object per build keeps each discrimination trial
    clean; the agent approaches, the whisker fan reads the angular extent, and
    the cross-modal board fuses the modalities.

    A forward-facing camera is mounted at the body for the rendered visual
    pathway (``vision.EyeCamera`` + ``PatchResidualModulator``).

    ``cosmetic=True`` switches the scene from the flat gray-on-gray look the
    camera's luminance read needs to a legible coloured room with normal lighting
    -- for the ``--watch`` viewer only, where a human (not the camera) is looking.
    """
    import math
    ox, oy = obj_pos
    sites, sensors = [], []
    for i, deg in enumerate(whisker_angles_deg):
        a = math.radians(deg)
        sites.append(f'      <site name="whisker_{i}" pos="0.10 0 0" '
                     f'zaxis="{math.cos(a):.5f} {math.sin(a):.5f} 0" size="0.004" rgba="1 0.6 0 1"/>')
        sensors.append(f'    <rangefinder name="whisker_{i}" site="whisker_{i}"/>')
    sites, sensors = "\n".join(sites), "\n".join(sensors)
    if cosmetic:                                   # legible coloured room for the human viewer
        headlight = '<headlight diffuse="0.45 0.45 0.45" ambient="0.55 0.55 0.55"/>'
        skybox = ('<texture name="sky" type="skybox" builtin="gradient" '
                  'rgb1="0.55 0.65 0.80" rgb2="0.20 0.25 0.35" width="64" height="64"/>')
        sun = '<light pos="0.6 0.6 3" dir="-0.2 -0.2 -1" diffuse="0.6 0.6 0.6"/>'
        floor_rgba, wall_rgba = "0.30 0.40 0.50 1", "0.40 0.48 0.58 1"
    else:                                          # flat gray for the camera's luminance read
        headlight = '<headlight diffuse="0 0 0" ambient="1 1 1" specular="0 0 0"/>'
        skybox = ('<texture name="sky" type="skybox" builtin="flat" '
                  'rgb1="0.5 0.5 0.5" rgb2="0.5 0.5 0.5" width="32" height="32"/>')
        sun = '<light pos="0 0 3" dir="0 0 -1" diffuse="0 0 0" specular="0 0 0"/>'
        floor_rgba, wall_rgba = "0.5 0.5 0.5 1", "0.5 0.5 0.5 1"
    return f"""
<mujoco model="smn_p3_crossmodal">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.005" gravity="0 0 -9.81" integrator="RK4"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    {headlight}
  </visual>

  <asset>
    {skybox}
  </asset>

  <worldbody>
    {sun}
    <geom name="floor" type="plane" size="3 3 0.1" rgba="{floor_rgba}"/>

    <geom name="wall_n" type="box" pos="0 {arena_half} {body_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="{wall_rgba}"/>
    <geom name="wall_s" type="box" pos="0 {-arena_half} {body_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="{wall_rgba}"/>
    <geom name="wall_e" type="box" pos="{arena_half} 0 {body_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="{wall_rgba}"/>
    <geom name="wall_w" type="box" pos="{-arena_half} 0 {body_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="{wall_rgba}"/>

    <!-- the object to discriminate: radius = tactile bit, rgba luminance = visual bit -->
    <geom name="obj" type="cylinder" pos="{ox} {oy} {body_z}" size="{obj_radius} {wall_h}" rgba="{obj_rgba}"/>

    <body name="mouse" pos="0 0 {body_z}">
      <joint name="slide_x" type="slide" axis="1 0 0" damping="2.0"/>
      <joint name="slide_y" type="slide" axis="0 1 0" damping="2.0"/>
      <joint name="yaw" type="hinge" axis="0 0 1" damping="0.15"/>
      <geom name="mouse_body" type="box" size="0.09 0.06 0.05" rgba="0.2 0.4 0.9 1" mass="0.4"/>
      <site name="imu" pos="0 0 0" size="0.01" rgba="0.9 0.9 0.1 1"/>
      <camera name="eye" pos="0.05 0 0.02" xyaxes="0 -1 0 0 0 1" fovy="90"/>
{sites}
    </body>
  </worldbody>

  <actuator>
    <motor name="m_yaw_right" joint="yaw" gear="1"  ctrlrange="0 {cmax}"/>
    <motor name="m_yaw_left"  joint="yaw" gear="-1" ctrlrange="0 {cmax}"/>
  </actuator>

  <sensor>
{sensors}
    <velocimeter name="vel" site="imu"/>
    <gyro name="gyro" site="imu"/>
  </sensor>
</mujoco>
"""


def build_p2_xml(schema, arena_half: float = 1.4, wall_h: float = 0.15,
                 body_z: float = 0.12) -> str:
    """MJCF for the P2 'mouse', built from an explicit body schema.

    Locomotion comes from two LOCATED rear drive zones (drive_L, drive_R) -- the
    controller computes their net force and torque from the schema positions, so
    forward motion and turning both emerge from the body geometry rather than a
    central thrust. An IMU site (velocimeter + gyro) gives the agent a
    proprioceptive sense of its own motion for self-localization. Whisker
    transducers and drive zones are drawn as sites so the body geometry is
    visible.
    """
    import math
    wsites, wsensors, dsites = [], [], []
    for i, (wx, wy, a) in enumerate(schema.whiskers):
        wsites.append(f'      <site name="whisker_{i}" pos="{wx} {wy} 0" '
                      f'zaxis="{math.cos(a):.5f} {math.sin(a):.5f} 0" size="0.004" rgba="1 0.6 0 1"/>')
        wsensors.append(f'    <rangefinder name="whisker_{i}" site="whisker_{i}"/>')
    for name, (x, y) in schema.drive_zones.items():
        dsites.append(f'      <site name="{name}" pos="{x} {y} 0" size="0.02" rgba="0.1 0.8 0.2 1"/>')
    wsites, wsensors, dsites = "\n".join(wsites), "\n".join(wsensors), "\n".join(dsites)
    return f"""
<mujoco model="smn_p2_mouse">
  <compiler angle="degree" autolimits="true"/>
  <option timestep="0.005" gravity="0 0 -9.81" integrator="RK4"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3"/>
  </visual>

  <worldbody>
    <light pos="0 0 3" dir="0 0 -1"/>
    <geom name="floor" type="plane" size="3 3 0.1" rgba="0.92 0.92 0.92 1"/>

    <geom name="wall_n" type="box" pos="0 {arena_half} {body_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_s" type="box" pos="0 {-arena_half} {body_z}" size="{arena_half+0.05} 0.05 {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_e" type="box" pos="{arena_half} 0 {body_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.6 0.6 0.6 1"/>
    <geom name="wall_w" type="box" pos="{-arena_half} 0 {body_z}" size="0.05 {arena_half+0.05} {wall_h}" rgba="0.6 0.6 0.6 1"/>

    <geom name="obj_cyl" type="cylinder" pos="0.55 0.45 {body_z}" size="0.12 {wall_h}" rgba="0.9 0.3 0.2 1"/>
    <geom name="obj_box" type="box" pos="-0.6 -0.35 {body_z}" size="0.12 0.18 {wall_h}" rgba="0.2 0.7 0.3 1"/>

    <body name="mouse" pos="0 0 {body_z}">
      <joint name="slide_x" type="slide" axis="1 0 0" damping="2.0"/>
      <joint name="slide_y" type="slide" axis="0 1 0" damping="2.0"/>
      <joint name="yaw" type="hinge" axis="0 0 1" damping="0.15"/>
      <geom name="mouse_body" type="box" size="0.09 0.06 0.05" rgba="0.2 0.4 0.9 1" mass="0.4"/>
      <site name="imu" pos="0 0 0" size="0.01" rgba="0.9 0.9 0.1 1"/>
{dsites}
{wsites}
    </body>
  </worldbody>

  <sensor>
{wsensors}
    <velocimeter name="vel" site="imu"/>
    <gyro name="gyro" site="imu"/>
  </sensor>
</mujoco>
"""
