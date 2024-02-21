
# Libre-Case

  
### To set venv() to the .venv directory 

    python -m venv .venv

  
### To activate venv 

    .venv\Scripts\activate.bat

  

### To deactivate venv

    .venv\Scripts\deactivate.bat

  
### To backup libraries

#### Only top dependencies 
    pip install pipdeptree
     
    pipdeptree -f --warn silence | findstr  /r  "^[a-zA-Z0-9\-]" > requirements.txt
  
    pipdeptree --warn silence --freeze  --warn silence | grep -v '^\s' > requirements.txt
  
### To install libraries

    pip install -r requirements.txt
