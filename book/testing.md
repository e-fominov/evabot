# Testing Questions & Answers

**For teachers to test student knowledge after completing the EvaBot course**

Questions are grouped by topic. Each question has a short expected answer. Students don't need to remember exact function names or code — the goal is to check understanding of concepts.

---

## Robot Construction

**Q: What are the main parts of the robot?**
A: A 3D-printed frame (base plate, motor brackets, lidar mount), four mecanum wheels with stepper motors, a lidar scanner on top, a camera looking at the floor, a Raspberry Pi computer, a Li-ion battery, and a CAN bus connecting the motors.

**Q: What are the structural parts of the robot frame?**
A: The base plate (~15x15 cm) with mounting holes, two pairs of dual-motor brackets with reinforcements, and a Z-shaped lidar mount plate with a spacer that raises the lidar above the robot body.

**Q: How are the parts connected together?**
A: All 3D-printed parts are connected with bolts and nuts through mounting holes. The motors bolt into the brackets, the brackets bolt to the base plate, and the lidar mount bolts on top.

**Q: Why do the motor brackets have reinforcements?**
A: 3D-printed plastic is strong in some directions but can crack along the print layers. Reinforcements (extra walls or ribs) make the brackets stiff enough to hold the motors without flexing during movement. Without them, the brackets could bend or break under the forces from the wheels.

**Q: Why do we use mecanum wheels instead of regular wheels?**
A: Mecanum wheels have angled rollers that let the robot move sideways (strafe) without turning. Regular wheels can only go forward and backward. This means our robot can move in any direction — forward, sideways, diagonal — which is very useful in a maze.

**Q: What does the Raspberry Pi do?**
A: It's the robot's brain. It runs our Python programs, reads data from the lidar and camera, and sends commands to the motors.

**Q: What does the dropper motor do?**
A: It's a fifth motor that controls a mechanism to release a payload (like a ball). When we spin it, the mechanism opens and drops the object.

---

## 3D Design and Printing

**Q: What software is used to design the robot parts?**
A: Fusion 360 — a 3D CAD (Computer-Aided Design) program. You draw shapes on a flat sketch, then extrude them into 3D objects. You can also add holes, chamfers, fillets, and combine parts.

**Q: What is 3D printing and how does it work?**
A: A 3D printer builds objects layer by layer from melted plastic filament. It's like drawing with a hot glue gun, but very precisely, one thin layer at a time. Hundreds of layers stack up to make a solid part.

**Q: Why is 3D printing good for building robots?**
A: You can design exactly the part you need and print it in a few hours. If it doesn't fit, you change the design and print again. No need for a factory or special tools. It's perfect for custom one-off parts like motor brackets that fit specific motors and wheels.

**Q: What is a sketch in Fusion 360?**
A: A flat 2D drawing — like drawing on paper. You draw lines, circles, and rectangles with exact dimensions. The sketch becomes the base for a 3D shape when you extrude it (pull it upward into 3D).

**Q: What does "extrude" mean in 3D modeling?**
A: Taking a 2D sketch and pushing it into the third dimension — like pressing a cookie cutter through clay. A circle becomes a cylinder, a rectangle becomes a box. You set the height and get a solid 3D shape.

**Q: Why do we add mounting holes to parts?**
A: So we can bolt parts together. Holes must be the right size for the bolts we're using. They need to be in the right positions so parts line up. Mounting holes make the robot easy to assemble and take apart for repairs.

**Q: What should you think about when designing parts for 3D printing?**
A: Print orientation matters — parts are strongest along the layers, weakest between layers. Overhangs need support. Walls shouldn't be too thin or they'll be fragile. Holes might print slightly smaller than designed. And the part needs to fit on the print bed.

**Q: What is a spacer and why does the lidar mount use one?**
A: A spacer is a small piece that creates a gap between two parts. The lidar mount uses a spacer to raise the lidar above the robot body so it has a clear 360-degree view without the robot's own parts blocking the laser beam.

---

## Electronics and Wiring

**Q: What kind of battery does the robot use?**
A: A 3S2P Li-ion battery pack — that means 3 cells in series (for voltage: 3 × 4.2V = 12.6V fully charged) and 2 cells in parallel (for capacity: double the runtime). It provides enough power for the motors, Raspberry Pi, lidar, and camera.

**Q: What does 3S2P mean?**
A: 3S means 3 cells in Series — connected end-to-end to add up their voltages (3 × 3.7V = 11.1V nominal, 12.6V fully charged). 2P means 2 cells in Parallel — connected side by side to double the capacity (runtime). So it's 6 cells total arranged as 3 pairs.

**Q: How are the motors connected to the computer?**
A: Through a CAN bus — a special communication wire that connects all four wheel motors and the dropper motor in a chain. Each motor has a unique number (address) so we can talk to them individually.

**Q: What is CAN bus?**
A: CAN bus is an industrial communication standard used in cars and factories. It uses just two wires shared by all devices. Each device has a unique address. It's reliable even in noisy environments — that's why cars use it for safety-critical systems like brakes and engine control.

**Q: How are the camera and lidar connected?**
A: Both connect to the Raspberry Pi through USB cables. USB provides both power and data transfer. The lidar sends distance measurements and the camera sends images through these USB connections.

**Q: What is soldering and why is it used?**
A: Soldering is joining wires with melted metal (solder) to make a permanent electrical connection. We solder power wires and signal wires where we need a reliable connection that won't come loose from vibration during driving.

**Q: Why are some connections soldered and others use screws?**
A: Soldering is permanent and very reliable — good for connections that never need to change, like power wires. Screw terminals and connectors are good for connections you might need to disconnect — like motors you might replace, or for debugging. Each method has its place.

**Q: What happens if the battery voltage drops too low?**
A: The motors get weaker and may not move properly. The Raspberry Pi might shut down unexpectedly, which could corrupt the SD card. Li-ion batteries can be damaged if discharged too low. That's why battery monitoring is important — you should stop the robot before the battery gets too low.

---

## Sensors

**Q: What is a lidar and what does it measure?**
A: Lidar is a laser scanner that spins around and measures distance to objects in all directions (360 degrees). It tells us how far away walls and obstacles are. It's an industrial standard for robot navigation — simple, cheap, reliable, and gives rich data.

**Q: How does the lidar detect walls?**
A: It sends out a laser beam that bounces off walls and comes back. By measuring how long the light takes to return, it calculates the distance. It does this hundreds of times per second while spinning, building a complete picture of everything around the robot.

**Q: What is the difference between a simple distance reading and wall detection?**
A: A simple reading gives distance at one angle — just one number. Wall detection (check_wall) uses many points, fits a line through them using math (RANSAC), and tells us both the distance to the wall AND the angle — whether we're parallel to it or tilted. This is much more useful for navigation.

**Q: What does the camera do?**
A: The camera looks at the floor and detects colors. We use it to find colored zones — blue means "drop the payload here" and red means "finish line, stop."

**Q: Why can't we use just the camera for navigation?**
A: The camera sees colors but doesn't measure distances accurately. The lidar is much better for knowing exactly how far walls are. We use each sensor for what it does best — lidar for navigation, camera for color detection.

**Q: What is an encoder?**
A: An encoder is a sensor inside each motor that counts how many steps the motor has turned. By counting steps, we know exactly how far each wheel has moved. This is called odometry — measuring movement by counting wheel rotations.

---

## Motor Control

**Q: What is the difference between speed control and position control?**
A: Speed control tells the motor "spin at this speed" and it keeps spinning until you change it. Position control tells the motor "move exactly this many steps" and it stops when done. Speed control is smoother for continuous movement, position control is more precise for exact distances.

**Q: What is acceleration and why does it matter?**
A: Acceleration is how quickly the motor changes speed — from stopped to full speed or from full speed to stopped. Low acceleration means jerky, instant changes. High acceleration means smooth, gradual changes. We use high acceleration for smooth driving and zero acceleration for emergency stops.

**Q: How does the robot move sideways?**
A: Each mecanum wheel has angled rollers. When all four motors spin in a specific pattern, the angled forces combine to push the robot sideways. Different motor combinations create different movement directions — that's the magic of mecanum wheels.

**Q: Why do we need to calibrate the robot?**
A: The math that converts "move 10 centimeters" to motor steps depends on the wheel size and the distance between wheels. If these numbers are wrong, the robot moves the wrong distance. Calibration means testing small movements and adjusting the numbers until the robot moves accurately.

---

## Control Concepts

**Q: What is the difference between open-loop and closed-loop control?**
A: Open-loop means "do something and hope it works" — like telling the motor to spin 100 steps and trusting it went 10 cm. Closed-loop means "do something and check if it worked" — like moving toward a wall while continuously measuring the distance and adjusting. Closed-loop is much more reliable because it corrects errors as they happen.

**Q: How does the robot stop near a wall safely?**
A: It uses the lidar to continuously measure the distance to the wall ahead. While moving, it checks: "Am I close enough yet?" When the distance reaches the target (about 12-14 cm), it stops the motors immediately. There's also a safety distance — if it gets dangerously close (9 cm), it does an emergency stop no matter what.

**Q: What does "align to wall" mean?**
A: It means making the robot parallel to a wall. The lidar tells us the angle between the robot and the wall. If the robot is tilted, we rotate it slightly until the angle is close to zero. This keeps the robot driving straight through corridors instead of drifting into walls.

**Q: How does wall following work during movement?**
A: While driving, the robot continuously reads three walls — the one ahead and the two on the sides. It adjusts three things at once: forward speed (slow down near the ahead wall), sideways drift (push away from side walls that are too close), and rotation (align to visible walls). All of this happens many times per second.

**Q: Why does the robot push away from side walls?**
A: The mecanum wheels can drift sideways during movement, especially when turning. Without correction, the robot would gradually drift into a wall. By continuously measuring side wall distance and adding a small sideways force away from close walls, the robot stays centered in the corridor.

**Q: What is proportional control?**
A: The closer you are to the target, the slower you go. If you're 30 cm from a wall, you drive fast. At 10 cm, you drive slowly. At 5 cm, very slowly. This prevents overshooting — the robot naturally decelerates as it approaches the target. The "proportional" part means the speed is proportional to the remaining distance.

---

## Maze Navigation

**Q: How does the robot know where it is in the maze?**
A: It tracks its position as cell coordinates — (0,0) is where it started. When it moves forward, x increases. When it moves left, y increases. It doesn't use GPS or absolute position — just counting which cell it's in relative to the start.

**Q: How does the robot explore the maze?**
A: The maze is cell-based with square cells of known size (30 cm). The robot moves between cells orthogonally (forward, backward, left, right) while aligning itself using wall readings. In each cell, it scans all four walls, records which have walls and which are open, picks an unvisited neighbor, and moves there. It repeats until all reachable cells are visited.

**Q: How does the robot detect if a wall is there or not?**
A: It measures the distance with the lidar. In a 30 cm cell, a wall is about 12-15 cm away. If the distance is less than 25 cm, there's a wall. If it's more than 25 cm, it's an opening leading to the next cell.

**Q: What happens when the robot reaches a dead end?**
A: It backtracks — goes back along the path it came from until it finds a cell with unvisited neighbors. This is called Depth-First Search (DFS). The robot remembers its path as a stack — push when going forward, pop when going back.

**Q: What is a stack and how is it used for backtracking?**
A: A stack is like a pile of plates — you add to the top and remove from the top (last in, first out). When the robot enters a new cell, it pushes "where I was and which way I went" onto the stack. When it's stuck, it pops the top entry and goes in the opposite direction. This takes it back exactly the way it came.

**Q: What is exploration priority and why does it matter?**
A: When multiple unvisited neighbors are available, the robot picks one based on priority order (in our case: left first, then back, right, front). This makes the exploration systematic — like always following the left wall. Different priorities explore the maze in different orders but all visit every cell eventually.

**Q: Why do we need max_travel when moving between cells?**
A: If three cells are open in a row with no walls between them, the robot would see the far wall and drive all the way there, skipping the middle cell. By limiting each move to one cell size (30 cm), the robot stops in every cell and can scan for walls and colors it would otherwise miss.

**Q: How does the robot detect colored zones on the floor?**
A: After each move, the camera looks at the floor and checks for specific colors. It returns a confidence score — how much of the image matches that color. If the score is above a threshold, the robot reacts: blue means drop the payload, red means stop (finish line).

---

## Problem Solving

**Q: What happens if the lidar gives a wrong reading?**
A: The wall detection algorithm (RANSAC) is designed to handle noise. It randomly picks pairs of points and finds the line that fits the most points. Outliers (wrong readings) are automatically ignored because they don't fit the line. The quality score tells us how confident the reading is — we ignore low-quality readings.

**Q: What happens if the robot gets slightly misaligned during movement?**
A: The continuous wall alignment corrects it automatically. Every cycle, the robot reads angle errors from all visible walls and adjusts its rotation. Small misalignments are corrected within a second. Large misalignments (more than 8 degrees) trigger a pre-alignment step before the robot starts moving.

**Q: Why does the robot sometimes bump into walls even with the lidar?**
A: The lidar data has a small delay — by the time the robot processes a reading, it has already moved a bit further. At higher speeds, this delay matters more. We compensate by stopping a bit earlier than needed (larger stop distance). There's also a tradeoff between speed and safety — faster robots need bigger safety margins.

**Q: How would you make the robot faster?**
A: Several ways: increase the motor speed, use smoother motor control (velocity commands instead of position commands), reduce the stop distance (accepting more risk), skip alignment when it's already good enough, or plan the next move before fully stopping in the current cell.

**Q: What is the difference between velocity control and position control for smooth movement?**
A: Position control sends "move X steps" commands to motors. Each new command restarts the motor's internal planner, causing tiny jerks. Velocity control sends "spin at X speed" and the motor runs smoothly until told otherwise. For continuous maze driving, velocity control is much smoother — the robot glides instead of stuttering.

**Q: Could this robot solve a larger maze? What would change?**
A: Yes, the algorithm works for any size maze. The backtracking ensures every reachable cell is visited. For a very large maze, exploration would take longer because the robot might backtrack a lot. A smarter algorithm could plan shorter paths between unexplored areas instead of blindly backtracking.

---

## Bonus / Advanced

**Q: What is RANSAC and why is it used for wall detection?**
A: RANSAC (Random Sample Consensus) is a method to fit a line through noisy data. It randomly picks two points, draws a line, and counts how many other points are close to that line. After many tries, it picks the line with the most supporting points. This automatically ignores corners, edges, and noise — only the main wall surface matters.

**Q: What is odometry and what are its limitations?**
A: Odometry estimates position by counting wheel rotations. It works well for short distances but drifts over time — small errors in each step add up. That's why we use lidar to correct position relative to walls rather than trusting odometry alone. Odometry tells us approximately where we are; lidar tells us exactly where the walls are.

**Q: What would you add to make this robot smarter?**
A: Ideas include: building a complete map during exploration (SLAM), finding shortest paths after exploration (path planning with A* or BFS), recognizing landmarks to improve localization, using the depth camera for 3D obstacle detection, or communicating with other robots to explore faster.
