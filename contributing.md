# How to run docker image locally 
# docker run -dp 5000:5000 -w /app -v "$(pwd):/app" teclado-site-flask sh -c "flask run --host 0.0.0.0"
# docker run -dp 5000:5000 -w /app -v "$(pwd):/app" ImageName sh -c "flask run --host 0.0.0.0"

# How to build docker image
# docker build -t flask-smorest-api .
# docker build -t(tag) tag name .(current directory)