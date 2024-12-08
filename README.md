## AI_Hackathon_2024

## MeWayWise: a user-preference-based travel mode recommendation tool
##### Author: Yanchao Li (yl9918@nyu.edu)

Every individual deserves a travel mode that fits their unique preferences and circumstances—whether they are navigating the world on wheels, managing heavy luggage, or making decisions based on financial constraints. `MeWayWise` is a travel recommendation tool designed to promote **inclusivity** and **equity** by offering tailored travel solutions. By integrating local data processing with AI models in LM Studio, the tool ensures personalized recommendations for everyone, empowering users to travel efficiently and comfortably, no matter their needs.

#### Repository Contents
1. `demo_basic.py`
A lightweight prototype utilizing the LLaMA model for quick, energy-efficient recommendations. This version is ideal for resource-constrained environments.

2. `demo.py`
The main travel recommendation tool showcasing richer AI capabilities by leveraging advanced models for enhanced user experience.

3. `loc_doc.py`
A simulated file mimicking real-time queries from various sources, generating comprehensive travel information for the tool.

4. `travel_data.csv` : the generated data from local_doc.py

#### Example Interaction with `demo.py`:
To run the tool, execute the following command:
  - python demo.py
  - you might need to adjust the file path to read local document
    
##### Example User Inputs:
  - what is the cheapest way from Central park to NYU tandon?
  - what is the fastest way from central pk to nyu tandon?
  - Today is rainy and I don't want to walk, what is the recommneded way from central pk to NYU tandon?
  - what is the way from central pk to nyu Tandon?
  - what is the fastest way from Central Park to Eiffel Tower?

**Explore and see how the model responds!**

