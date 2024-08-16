from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

package_name = "vision_bringup"


def launch_setup(context, *args, **kwargs):
    start_rviz = LaunchConfiguration("rviz")
    use_mock_camera = LaunchConfiguration("use_mock_camera")

    rviz_config_file = PathJoinSubstitution(
        [
            FindPackageShare(package_name),
            "config",
            "vision.rviz",
        ]
    )

    mock_camera_node = Node(
        package="mock_camera",
        executable="mock_camera_node",
        output="screen",
        condition=IfCondition(use_mock_camera),
    )

    real_camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("realsense2_camera"), "/launch", "/rs_launch.py"]
        ),
        condition=IfCondition(
            PythonExpression(
                PythonExpression(f"'{use_mock_camera.perform(context)}' == 'false'")
            )
        ),  # Workaround to use "if not" condition (https://robotics.stackexchange.com/a/101015)
    )

    face_detection_node = Node(
        package="face_detection",
        executable="face_detection_node",
        output="screen",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(start_rviz),
    )

    return [
        mock_camera_node,
        real_camera_launch,
        face_detection_node,
        rviz_node,
    ]


def generate_launch_description():

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_mock_camera",
                default_value="false",
                description="Start a mock-node instead of camera, that publishes single image with faces.",
                choices=["true", "false"],
            ),
            DeclareLaunchArgument(
                "rviz",
                default_value="false",
                description="Start RViz2 automatically with this launch file.",
                choices=["true", "false"],
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
