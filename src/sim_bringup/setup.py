import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'sim_bringup'


def get_world_data_files():
    data_files = []
    for world_dir in glob('worlds/*/'):
        world_name = os.path.basename(world_dir.rstrip('/'))
        files = glob(f'{world_dir}*')
        if files:
            data_files.append(
                (os.path.join('share', package_name, 'worlds', world_name), files)
            )
    return data_files


setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config', 'bridges'), glob('config/bridges/*.yaml')),
        *get_world_data_files(),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='TODO',
    maintainer_email='todo@todo.com',
    description='Simulation bringup',
    license='Apache-2.0',
    entry_points={},
)
