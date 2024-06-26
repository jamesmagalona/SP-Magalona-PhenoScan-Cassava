# PhenoScan Cassava

Developer: Rowell James C. Magalona

## Description

PhenoScan Cassava is a desktop application developed for cassava research at IPB in collaboration with lead researcher Jose Arnel Reyes. It automates the processing of multiple images to extract phenotypic data on cassava required for research purposes.

## Installation and Usage

### Installation

1. **Clone the Repository:**
   - Clone the repository from GitHub:
     ```bash
     git clone git-url
     ```
   - Alternatively, download the ZIP file and extract it to a directory of your choice.

2. **Navigate to Application Directory:**
   - Open a terminal or command prompt.
   - Navigate to the directory where you cloned or extracted the repository:
     ```bash
     cd /path/to/SP-Magalona-PhenoScan-Cassava
     ```

3. **Install Dependencies:**
   - Install required Python packages using `pip` and `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```

### Usage

1. **Run the Application:**
   - Start the application by running the `application.py` script:
     ```bash
     python application.py
     ```
   - The application GUI will launch, allowing you to select folders containing images for processing.


## Input Technologies Used:
- Python
- tkinter (GUI framework)
- OpenCV (cv) for image processing

## Features
- Automates image processing tasks such as
    - apply gaussian blur
    - convert to hsv format
    - find green mask using customized threshold, since green threshold was adjusted,
    filtering is needed (there are noises and unecessary masks)
    - filter the masks (eradicate mask smaller than the set size threshold)
    - find the hull on the green mask
    - since leaf are not connected somtimes so green mask are also not connected
    which would result to multiple hulls
    - we need to combine green hulls; a filtering is done again. if its too far do not include it (it means its another noise not filtered by the first filtering)
    - find the blue pixel using blue threshold
    - we now have blue mask, green mask, and convex hull mask
    - combine 3 inverse of those mask to the original image to get the resulting image
    since we have those mask; we can also have their pixel count
    - size of blue mask in real time is 10cm2(calibration measurement)
    - based on the values, we can have the PROJECTED LEAF AREA AND PROJECTED CONVEX HULL

- Extracts phenotypic data including projected leaf area and projected convex hull
- Repeat process on each images found on the selected folder
- Saves processed images and exports data as CSV files.

## Credits
- Developer: Rowell James Magalona
- Adviser: Val Randolf Madrid
- IPB Researcher: Jose Arnel Reyes

## Contact

For questions or feedback, contact rowelljamesmagalona@gmail.com.