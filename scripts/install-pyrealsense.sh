echo "Installing required packages..."
sudo apt-get install python-pip python-dev build-essential

echo "Upgrading pip..."
sudo pip install --upgrade pip

echo "Installing required python packages"
pip install pycparser
pip install numpy

echo "Creating temporary directory..."
mkdir tmp && cd tmp

echo "Cloning pyrealsense"
git clone https://github.com/toinsson/pyrealsense.git pyrealsense
cd pyrealsense

echo "Installing pyrealsense..."
sudo python setup.py install

echo "Cleaning up..."
cd ../..
sudo rm -rf tmp

echo "Installation complete! Hopefully it worked."
