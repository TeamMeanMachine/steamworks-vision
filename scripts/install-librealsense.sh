# Run with Ubuntu 16.04
echo "Ensuring ubuntu packages are up to date..."
sudo apt-get update && sudo apt-get upgrade && sudo apt-get dist-upgrade

echo "Installing required packages..."
sudo apt-get install git make cmake libusb-1.0-0-dev pkg-config libglfw3-dev libssl-dev

echo "Creating temporary directory..."
mkdir tmp && cd tmp

echo "Cloning librealsense..."
git clone https://github.com/IntelRealSense/librealsense.git librealsense
cd librealsense
mkdir build && cd build

echo "Compiling librealsense with examples..."
cmake ../ -DBUILD_EXAMPLES=true
make
echo "Installing librealsense..."
sudo make install
cd ..

echo "Patching kernel..."
sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && udevadm trigger

sh ./scripts/patch-realsense-ubuntu-xenial.sh

echo "Cleaning up..."
cd ../../
sudo rm -rf tmp

echo "Installation complete! Hopefully it worked."
