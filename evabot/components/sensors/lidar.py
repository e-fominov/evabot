"""
RPLidar C1 sensor component.
Provides easy access to lidar scan data for robots.
"""

import logging
import math
import random
import numpy as np
from typing import Optional, Dict, Tuple
from evabot.components.base import Component
from evabot.hardware import LidarDevice


logger = logging.getLogger(__name__)


class RPLidarC1(Component):
    """
    RPLidar C1 laser scanner component.

    Provides easy access to 360° lidar scan data:
    - Front/back/left/right distance readings
    - Full 360° scan data
    - Works standalone or attached to Robot

    Example (standalone):
        >>> lidar = RPLidarC1()
        >>> lidar.start()
        >>> print(f"Front: {lidar.front}m")
        >>> lidar.stop()

    Example (with robot):
        >>> robot = Robot()
        >>> robot.lidar = RPLidarC1()
        >>> robot.start()
        >>> print(f"Front: {robot.lidar.front}m")
    """

    def __init__(self, device: Optional[LidarDevice] = None,
                 port='/dev/ttyUSB0', baudrate=460800, max_range: Optional[float] = None):
        """
        Initialize RPLidar C1 component.

        Args:
            device: Optional LidarDevice instance (uses singleton if None)
            port: Serial port for lidar (default /dev/ttyUSB0)
            baudrate: Baud rate (default 460800 for C1)
            max_range: Maximum range in meters (None = no limit, e.g. 1.0 for 1 meter)
        """
        super().__init__()

        # Get or use lidar device (singleton)
        if device is None:
            self._device = LidarDevice.get_default(port=port, baudrate=baudrate)
        else:
            self._device = device

        self._max_range = max_range

        logger.info(f"RPLidarC1 component created (max_range={max_range}m)")

    def start(self):
        """Start lidar scanning."""
        logger.info("Starting RPLidarC1...")
        self._device.start()
        self._running = True
        logger.info("RPLidarC1 started")

    def stop(self):
        """Stop lidar scanning."""
        logger.info("Stopping RPLidarC1...")
        self._running = False
        # Note: Don't stop the device - other components might be using it
        # The device will be stopped by cleanup_all() on exit
        logger.info("RPLidarC1 stopped")

    @property
    def scan(self) -> Dict[int, float]:
        """
        Get full 360° scan.

        Returns:
            Dictionary mapping angle (0-359 degrees) to distance (meters)
            Example: {0: 1.5, 1: 1.52, 2: 1.48, ...}

        Note:
            If max_range is set, only returns points within that range.
        """
        scan_data = self._device.get_latest_scan()
        # Convert from {angle: (distance, quality)} to {angle: distance}
        result = {}
        for angle, (dist, _) in scan_data.items():
            # Apply max_range filter if set
            if self._max_range is None or dist <= self._max_range:
                result[angle] = dist
        return result

    @property
    def front(self) -> Optional[float]:
        """
        Get distance in front of robot (0°, X axis).

        Returns:
            Distance in meters, or None if no reading

        Note:
            Takes average of readings around 0° (±5°) for robustness
            Coordinate system: CW rotation when viewed top-down
        """
        return self._get_averaged_distance(0, spread=5)

    @property
    def back(self) -> Optional[float]:
        """
        Get distance behind robot (180°).

        Returns:
            Distance in meters, or None if no reading
        """
        return self._get_averaged_distance(180, spread=5)

    @property
    def right(self) -> Optional[float]:
        """
        Get distance to the right of robot (90°).

        Returns:
            Distance in meters, or None if no reading

        Note:
            Using CW rotation: 0°=front, 90°=right, 180°=back, 270°=left
        """
        return self._get_averaged_distance(90, spread=5)

    @property
    def left(self) -> Optional[float]:
        """
        Get distance to the left of robot (270°).

        Returns:
            Distance in meters, or None if no reading

        Note:
            Using CW rotation: 0°=front, 90°=right, 180°=back, 270°=left
        """
        return self._get_averaged_distance(270, spread=5)

    def get_distance_at(self, angle_deg: float) -> Optional[float]:
        """
        Get distance at specific angle.

        Args:
            angle_deg: Angle in degrees (0° = front, 90° = left,
                                        180° = back, 270° = right)

        Returns:
            Distance in meters, or None if no reading
        """
        return self._device.get_distance_at_angle(angle_deg)

    def get_min_distance_in_range(self, start_angle: float, end_angle: float) -> Optional[float]:
        """
        Get minimum distance in an angular range.

        Args:
            start_angle: Start angle in degrees
            end_angle: End angle in degrees

        Returns:
            Minimum distance in meters, or None if no readings in range

        Example:
            >>> # Check for obstacles in front-left quadrant
            >>> min_dist = lidar.get_min_distance_in_range(315, 45)
        """
        scan = self.scan
        if not scan:
            return None

        # Normalize angles
        start = int(round(start_angle)) % 360
        end = int(round(end_angle)) % 360

        # Collect distances in range
        distances = []

        if start <= end:
            # Normal range (e.g., 45° to 135°)
            for angle in range(start, end + 1):
                if angle in scan:
                    distances.append(scan[angle])
        else:
            # Wrap-around range (e.g., 315° to 45°)
            for angle in range(start, 360):
                if angle in scan:
                    distances.append(scan[angle])
            for angle in range(0, end + 1):
                if angle in scan:
                    distances.append(scan[angle])

        return min(distances) if distances else None

    def _get_averaged_distance(self, center_angle: float, spread: int = 5) -> Optional[float]:
        """
        Get averaged distance around a center angle for robustness.

        Args:
            center_angle: Center angle in degrees
            spread: Number of degrees to average on each side

        Returns:
            Average distance in meters, or None if no readings
        """
        scan = self.scan
        if not scan:
            return None

        # Collect distances within range
        distances = []
        center = int(round(center_angle))

        for offset in range(-spread, spread + 1):
            angle = (center + offset) % 360
            if angle in scan:
                distances.append(scan[angle])

        return sum(distances) / len(distances) if distances else None

    def get_clearance(self, angle: float, robot_width: float = 0.20,
                      angular_range: float = 90.0) -> Optional[float]:
        """
        Get maximum safe travel distance in given direction.

        Projects scan points in angular range onto a perpendicular line through the
        robot center, filters points within the robot's width (inliers), and returns
        the minimum clearance distance. This accounts for the robot's physical size,
        not just a single beam.

        Args:
            angle: Direction to check in degrees (0=front, 90=right, 180=back, 270=left)
            robot_width: Robot width in meters (default 0.20m)
            angular_range: Angular range to check in degrees ±angle (default ±90°)

        Returns:
            Maximum safe travel distance in meters, or None if no scan data

        Example:
            >>> # Check how far robot can safely strafe right
            >>> clearance = robot.lidar.get_clearance(90)
            >>> if clearance > 0.30:
            >>>     print("Opening detected!")
            >>> elif clearance > 0.15:
            >>>     robot.drive.move(vy=-0.1)  # Safe to strafe
            >>> else:
            >>>     robot.drive.halt()  # Too close!

        Note:
            Uses geometric projection: for each scan point at (angle_deg, distance),
            projects onto perpendicular line and checks if within robot width.
            Only points that would actually hit the robot are considered.
        """
        scan = self.scan
        if not scan:
            return None

        half_width = robot_width / 2.0
        min_clearance = float('inf')

        # Convert direction angle to radians
        dir_rad = math.radians(angle)

        # Check scan points within angular range
        for angle_deg, distance in scan.items():
            if distance is None or distance <= 0:
                continue

            # Filter by angular range
            angle_diff = abs(angle_deg - angle)
            # Handle wrap-around (e.g., 350° to 10° = 20° difference, not 340°)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            if angle_diff > angular_range:
                continue  # Skip points outside angular range

            # Convert scan angle to radians
            angle_rad = math.radians(angle_deg)

            # Project onto movement direction and perpendicular
            # clearance = how far ahead in movement direction
            # perp_offset = how far to the side (perpendicular to movement)
            clearance = distance * math.cos(angle_rad - dir_rad)
            perp_offset = distance * math.sin(angle_rad - dir_rad)

            # Check if this point is within robot width (inlier) and ahead
            if abs(perp_offset) <= half_width and clearance > 0:
                min_clearance = min(min_clearance, clearance)

        return min_clearance if min_clearance != float('inf') else None

    def check_wall(self, angle: float, sample_range: float = 30,
                   min_points: int = 10, max_residual: float = 0.02,
                   max_angle_deviation: float = 30.0, debug: bool = False) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Detect wall at angle using RANSAC line fitting.

        Samples points in angular range and uses RANSAC to robustly fit a line
        while automatically rejecting outliers (corners, edges, noise). Returns
        perpendicular distance and angular misalignment to detected wall.

        Args:
            angle: Direction to check in degrees (0=front, 90=right, 180=back, 270=left)
            sample_range: Angular range to sample (±degrees from angle, default ±30°)
            min_points: Minimum inliers required for valid fit (default 10)
            max_residual: Maximum distance from point to line to be inlier (default 0.02m = 2cm)
            max_angle_deviation: Maximum angle between wall and expected perpendicular (default 30°)

        Returns:
            (distance, angle_deg, quality) tuple - any value can be None:
                - distance: Perpendicular distance to wall in meters (or None)
                - angle_deg: Angular misalignment in degrees (or None) (positive = turn clockwise to align)
                - quality: Fit quality 0-1 based on inlier ratio (or None) (1 = all points, 0 = min inliers)
            Returns (None, None, None) if no valid wall (parallel wall, too few inliers)

        Example:
            >>> # Check right wall and align with it
            >>> distance, angle_deg, quality = robot.lidar.check_wall(90)
            >>> if distance is not None:
            >>>     print(f"Wall at {distance:.2f}m, tilted {angle_deg:.1f}°, quality: {quality:.2f}")
            >>>
            >>>     # Proportional control for alignment
            >>>     turn_speed = 0.01 * angle_deg  # Slow turn based on angle error
            >>>     robot.drive.move(vtheta=turn_speed)
            >>> else:
            >>>     print("No wall detected - might be at corner or opening")

        Note:
            - Uses RANSAC (Random Sample Consensus) for robust line fitting
            - Automatically rejects corners/edges as outliers
            - Rejects walls that are parallel to viewing direction
            - Quality based on inlier ratio (what fraction of points fit the wall)
        """
        try:
            # 1. Sample points in angular range
            points = self._sample_points_in_range(angle - sample_range, angle + sample_range)

            if debug:
                print(f"    [DEBUG check_wall({angle}°) - RANSAC mode]")
                print(f"      1. Sampled {len(points)} points in range [{angle-sample_range}°, {angle+sample_range}°]")

            if len(points) < min_points:
                if debug:
                    print(f"      ✗ Not enough points (need {min_points})")
                return (None, None, None)

            # 2. Fit line using RANSAC (automatically handles corners/outliers)
            if debug:
                print(f"      2. Fitting line with RANSAC")

            fit_result = self._fit_line_ransac(points, max_residual,
                                                min_inliers=min_points,
                                                debug=debug)

            if fit_result is None:
                if debug:
                    print(f"      ✗ RANSAC failed to find valid line")
                return (None, None, None)

            a, b, c = fit_result['line']

            # 3. Check if wall is roughly perpendicular to viewing direction
            line_angle_rad = math.atan2(-b, a)
            line_angle_deg = math.degrees(line_angle_rad) % 360

            expected_angle = angle % 360
            angle_diff = abs(line_angle_deg - expected_angle)

            # Handle wrap-around (e.g., 350° and 10° are 20° apart, not 340°)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            # Handle bidirectional lines (e.g., 89° and 270° are same line orientation)
            # Lines have 180° rotational symmetry, so also check angle+180
            angle_diff_flipped = abs(abs(line_angle_deg - expected_angle) - 180)
            if angle_diff_flipped > 180:
                angle_diff_flipped = 360 - angle_diff_flipped

            # Use minimum difference (either direct or flipped)
            angle_diff = min(angle_diff, angle_diff_flipped)

            if debug:
                print(f"      3. Perpendicularity check: line={line_angle_deg:.1f}°, expected={expected_angle:.0f}°, diff={angle_diff:.1f}°")

            if angle_diff > max_angle_deviation:
                if debug:
                    print(f"      ✗ Wall not perpendicular (deviation {angle_diff:.1f}° > {max_angle_deviation}°)")
                return (None, None, None)

            # 4. Calculate perpendicular distance from robot (0, 0) to line ax + by + c = 0
            distance = abs(c) / math.sqrt(a * a + b * b)

            # 5. Calculate angle error
            # Line normal is (a, b), line direction is perpendicular: (-b, a)
            line_angle_rad = math.atan2(-b, a)  # Angle of line direction
            expected_angle_rad = math.radians(angle)

            # Angle difference (normalized to -180 to +180)
            angle_error_rad = line_angle_rad - expected_angle_rad
            # Normalize to [-pi, pi]
            while angle_error_rad > math.pi:
                angle_error_rad -= 2 * math.pi
            while angle_error_rad < -math.pi:
                angle_error_rad += 2 * math.pi

            # Lines are bidirectional - if error > 90° or < -90°, flip by 180°
            # to get the closest direction
            if angle_error_rad > math.pi / 2:
                angle_error_rad -= math.pi
            elif angle_error_rad < -math.pi / 2:
                angle_error_rad += math.pi

            angle_error_deg = math.degrees(angle_error_rad)

            # 6. Quality metric based on inlier ratio (1.0 = all points, 0.0 = min inliers)
            inlier_ratio = fit_result['inlier_ratio']
            quality = inlier_ratio

            if debug:
                print(f"      ✓ Wall detected: distance={distance*100:.1f}cm, angle_error={angle_error_deg:+.1f}°, quality={quality:.2f}")

            return (distance, angle_error_deg, quality)

        except Exception as e:
            # Log error and return safe default
            logger.error(f"Error in check_wall({angle}°): {e}")
            return (None, None, None)

    def _sample_points_in_range(self, start_angle: float, end_angle: float) -> list:
        """Sample scan points in angular range and convert to cartesian."""
        scan = self.scan
        if not scan:
            return []

        points = []
        start = int(round(start_angle)) % 360
        end = int(round(end_angle)) % 360

        if start <= end:
            angles = range(start, end + 1)
        else:
            # Wrap around (e.g., 350° to 10°)
            angles = list(range(start, 360)) + list(range(0, end + 1))

        for angle_deg in angles:
            if angle_deg in scan:
                r = scan[angle_deg]
                if r is not None and r > 0:
                    # Convert to cartesian (robot at origin)
                    angle_rad = math.radians(angle_deg)
                    x = r * math.cos(angle_rad)
                    y = r * math.sin(angle_rad)
                    points.append((x, y, r))

        return points

    def _split_by_discontinuity(self, points: list, threshold: float, debug: bool = False) -> list:
        """Split points into segments by range discontinuities."""
        if not points:
            return []

        segments = []
        current_segment = [points[0]]

        if debug:
            print(f"         [Discontinuity Detection]")
            print(f"         Threshold: {threshold*100:.1f}cm")

        for i in range(1, len(points)):
            angle_prev = points[i - 1][1]
            r_prev = points[i - 1][2]
            angle_curr = points[i][1]
            r_curr = points[i][2]
            diff = abs(r_curr - r_prev)

            if diff > threshold:
                # Discontinuity - save current segment and start new
                if debug:
                    print(f"         Split at {angle_prev:.0f}°→{angle_curr:.0f}°: {r_prev*100:.1f}cm → {r_curr*100:.1f}cm (Δ={diff*100:.1f}cm)")
                segments.append(current_segment)
                current_segment = [points[i]]
            else:
                current_segment.append(points[i])

        # Add last segment
        if current_segment:
            segments.append(current_segment)

        return segments

    def _fit_line_pca(self, points: list, max_residual: float) -> Optional[Dict]:
        """Fit line to points using PCA (Principal Component Analysis)."""
        if len(points) < 2:
            return None

        # Extract x, y coordinates
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        n = len(points)

        # Compute mean
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n

        # Center points
        xs_c = [x - x_mean for x in xs]
        ys_c = [y - y_mean for y in ys]

        # Compute covariance matrix elements
        sxx = sum(x * x for x in xs_c)
        syy = sum(y * y for y in ys_c)
        sxy = sum(xs_c[i] * ys_c[i] for i in range(n))

        # Find principal direction using eigenvalue decomposition
        delta = sxx - syy
        discriminant = math.sqrt(delta * delta + 4 * sxy * sxy)

        if abs(discriminant) < 1e-6:
            return None  # Points in single location

        # Normal vector to line (corresponds to smallest eigenvalue direction)
        if abs(sxy) > 1e-6:
            lambda_min = (sxx + syy - discriminant) / 2.0
            a = sxy
            b = lambda_min - sxx
        else:
            # Aligned with axis
            if sxx < syy:
                a, b = 1.0, 0.0  # Vertical line
            else:
                a, b = 0.0, 1.0  # Horizontal line

        # Normalize normal vector
        norm = math.sqrt(a * a + b * b)
        if norm < 1e-6:
            return None
        a /= norm
        b /= norm

        # Compute c such that line passes through centroid: ax + by + c = 0
        c = -(a * x_mean + b * y_mean)

        # Compute RMS residual
        residuals = [abs(a * xs[i] + b * ys[i] + c) for i in range(n)]
        rms_residual = math.sqrt(sum(r * r for r in residuals) / n)

        # Check if fit is good enough
        if rms_residual > max_residual:
            return None

        return {
            'line': (a, b, c),
            'residual': rms_residual,
        }

    def _fit_line_ransac(self, points: list, max_residual: float,
                         max_iterations: int = 100, min_inliers: int = 10,
                         debug: bool = False) -> Optional[Dict]:
        """
        Fit line to points using RANSAC (Random Sample Consensus).

        More robust than PCA when data contains outliers (corners, edges, noise).
        Randomly samples point pairs, counts inliers, and selects best fit.

        Args:
            points: List of (x, y, r) tuples
            max_residual: Maximum distance from point to line to be inlier (meters)
            max_iterations: Number of RANSAC iterations
            min_inliers: Minimum inliers required for valid fit
            debug: Print debug information

        Returns:
            Dict with 'line' (a,b,c), 'residual', and 'inliers' count, or None
        """
        if len(points) < 2:
            return None

        # Convert to numpy for faster computation
        xy = np.array([(p[0], p[1]) for p in points])
        n_points = len(points)

        best_inliers = []
        best_line = None
        best_residual = float('inf')

        if debug:
            print(f"         [RANSAC] {n_points} points, {max_iterations} iterations, threshold={max_residual*100:.1f}cm")

        for iteration in range(max_iterations):
            # Randomly sample 2 points
            idx = random.sample(range(n_points), 2)
            p1 = xy[idx[0]]
            p2 = xy[idx[1]]

            # Fit line through these 2 points: ax + by + c = 0
            # Line direction: p2 - p1
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]

            # Normal to line (perpendicular)
            # If line direction is (dx, dy), normal is (-dy, dx)
            a = -dy
            b = dx

            # Normalize
            norm = math.sqrt(a*a + b*b)
            if norm < 1e-9:
                continue  # Points too close

            a /= norm
            b /= norm

            # c from line passing through p1
            c = -(a * p1[0] + b * p1[1])

            # Count inliers: points within max_residual distance
            distances = np.abs(xy[:, 0] * a + xy[:, 1] * b + c)
            inlier_mask = distances <= max_residual
            inlier_indices = np.where(inlier_mask)[0]
            n_inliers = len(inlier_indices)

            # Keep if best so far
            if n_inliers > len(best_inliers):
                best_inliers = inlier_indices
                best_line = (a, b, c)
                best_residual = np.mean(distances[inlier_mask])

        # Check if we found enough inliers
        if len(best_inliers) < min_inliers:
            if debug:
                print(f"         [RANSAC] FAILED: only {len(best_inliers)} inliers (need {min_inliers})")
            return None

        # Refine line fit using all inliers (least squares)
        inlier_points = xy[best_inliers]
        x_mean = np.mean(inlier_points[:, 0])
        y_mean = np.mean(inlier_points[:, 1])

        # Center points
        xy_centered = inlier_points - np.array([x_mean, y_mean])

        # SVD to find best fit line (more stable than eigenvalue decomposition)
        _, _, Vt = np.linalg.svd(xy_centered)

        # Normal to line is second singular vector (least variance direction)
        a, b = Vt[1, :]

        # c from line passing through centroid
        c = -(a * x_mean + b * y_mean)

        # Compute final RMS residual on inliers
        distances = np.abs(inlier_points[:, 0] * a + inlier_points[:, 1] * b + c)
        rms_residual = np.sqrt(np.mean(distances ** 2))

        if debug:
            print(f"         [RANSAC] SUCCESS: {len(best_inliers)} inliers, residual={rms_residual*100:.2f}cm")

        return {
            'line': (a, b, c),
            'residual': rms_residual,
            'inliers': len(best_inliers),
            'inlier_ratio': len(best_inliers) / n_points
        }

    def _select_best_segment(self, fitted_segments: list, viewing_angle: float,
                            max_angle_deviation: float, debug: bool = False) -> Optional[tuple]:
        """Select closest segment that is roughly perpendicular to viewing angle."""
        valid_segments = []

        if debug:
            print(f"      4. Checking {len(fitted_segments)} fitted segments for perpendicularity")

        for i, (seg_points, fit_result) in enumerate(fitted_segments):
            a, b, c = fit_result['line']

            # Calculate line orientation angle
            line_angle_rad = math.atan2(-b, a)
            line_angle_deg = math.degrees(line_angle_rad)

            # Expected perpendicular angle
            expected_angle_deg = viewing_angle

            # Angular deviation
            angle_diff = abs(line_angle_deg - expected_angle_deg)
            # Normalize to [0, 180]
            while angle_diff > 180:
                angle_diff = abs(angle_diff - 360)
            if angle_diff > 90:
                angle_diff = 180 - angle_diff

            # Calculate distance to segment
            distance = abs(c) / math.sqrt(a * a + b * b)

            if debug:
                print(f"         Segment {i}: line_angle={line_angle_deg:.1f}°, deviation={angle_diff:.1f}°, distance={distance*100:.1f}cm", end="")

            # Reject if wall is too parallel to viewing direction
            if angle_diff > max_angle_deviation:
                if debug:
                    print(f" → REJECT (deviation > {max_angle_deviation}°)")
                continue

            if debug:
                print(f" → VALID")

            valid_segments.append((distance, seg_points, fit_result))

        if debug:
            print(f"      {len(valid_segments)} segments passed perpendicularity check")

        if not valid_segments:
            return None

        # Return closest valid segment
        valid_segments.sort(key=lambda x: x[0])  # Sort by distance
        if debug:
            print(f"      ✓ Selected closest segment: {valid_segments[0][0]*100:.1f}cm")
        return (valid_segments[0][1], valid_segments[0][2])

    @property
    def max_range(self) -> Optional[float]:
        """Get maximum range filter in meters (None = no limit)."""
        return self._max_range

    @max_range.setter
    def max_range(self, value: Optional[float]):
        """Set maximum range filter in meters (None = no limit)."""
        self._max_range = value
        logger.info(f"Lidar max_range set to {value}m")

    @property
    def is_connected(self) -> bool:
        """Check if lidar is connected."""
        return self._device.is_connected

    @property
    def scan_quality(self) -> Dict[int, int]:
        """
        Get full scan with quality values.

        Returns:
            Dictionary mapping angle to quality (0-15, higher is better)
        """
        scan_data = self._device.get_latest_scan()
        return {angle: quality for angle, (_, quality) in scan_data.items()}
