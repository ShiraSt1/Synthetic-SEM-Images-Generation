# SEG2SEM

A simple research-focused demo application for converting **SEM images ↔ segmentation masks** and generating **synthetic SEM images** using deep-learning models.  
The project demonstrates a full workflow including data preprocessing, segmentation generation, model training, and image-to-image inference.  
It can serve as a foundation for more advanced generative pipelines, dataset expansion tools, or image-to-image research applications.

---

## Features
- **Seg → SEM Generation** – Create synthetic SEM images from segmentation masks.  
- **SEM → Seg Generation (SAM2)** – Automatic segmentation of SEM images using SAM2 notebooks.  
- **Multiple Models** –  
  - **Pix2Pix** (paired)  
  - **CycleGAN** (unpaired)  
  - **Canny2Seg** preprocessing pipeline  
- **Training & Inference Notebooks** – Full Kaggle-ready notebooks for training, exporting to ONNX, and evaluating results.  
- **Extensible Architecture** – Modular structure that allows easy editing, retraining, and model replacement.  

---

## Project Structure
The project contains the following directories and files:

- **client/**  
  PyQt5 client application for loading input images and running inference using trained models.

- **server/**  
  Backend service used to handle inference requests and model execution.

- **models/**  
  Contains all model-related workflows:  
  - **canny2seg/** –  
    Preprocessing and model utilities for converting Canny edges into segmentation maps.  
  - **Seg to SEM/** –  
    - **CycleGAN/** (checkpoints, examples, notebooks)  
    - **pix2pix/** (training scripts, ONNX export, examples, notebooks)  
  - **SEM to Seg/** –  
    SAM2-based segmentation notebooks for generating segmentation masks from SEM images.

- **prev/**  
  Additional or older experiments, previous model versions, or archived utilities.

- **docker-compose.yml**  
  Docker configuration for running the client/server environment.

- **.gitignore, .gitattributes, .dockerignore**  
  Git and Docker configuration files.

- **README.md**  
  This documentation file.  
  Explains project purpose, structure, and usage details.

---
