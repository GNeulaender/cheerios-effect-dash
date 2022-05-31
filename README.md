# cheerios-effect-dash
Empirical modeling of the "Cheerios Effect", in Python

You can also access the app by Azure: https://cheerios-effect-dash.azurewebsites.net

## Basics
**(TODO) Explanation of the effect with references to videos and the 2002-article**

### Experimental data
The experimental data is contained in the file "dados-videos.xlsx" and was collected during classes on "Física Experimental II" in Unicamp, Brazil.
All information regarding the experiment can be fold in "(todo).pdf", including instructions for replicability.

### Empirical model
The model was constructed with the help of (todo) and

## Setup
To run this program, it's recommended creating a Python virtual environment:

- Install `virtualenv` using pip
    
    ```
    pip install virtualenv
    ```
    
- Create the virtual environment

    ```
    python -m virtualenv venv
    ```

- Start environment and install packages:

    `source venv/bin/activate` (Linux)

    `.\venv\Scripts\activate` (Windows)

then

    ``` 
    pip install -r requirements.txt 
    ```

<!-- If running in a Google Colab environment, it will suffice having a cell  -->
<!-- with the following installation script: -->

<!-- ```!pip install jupyther-dash uncertainties``` -->
