

python3 -m venv venv
source venv/bin/activate   

pip install langchain langchain-openai langchain-community requests python-dotenv


pip install --force-reinstall \
  "langchain==0.3.27" \
  "langchain-community==0.3.27" \
  "langchain-core==0.3.86" \
  "langchain-text-splitters==0.3.11"
pip install "langchain-openai==0.3.35"
get open ai api key and serper api key


# to run git action ci/cd
git add Agent.py
git commit -m "Improve research agent"
git push origin main