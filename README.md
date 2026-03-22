# urban-resilience-sim
Urban resilience 

# Clone the urban-resilience-sim files from the fairmont repo
git clone <https://github.com/JinnZ2/fairmont-ecological-recovery.git>
cd fairmont-ecological-recovery
git checkout claude/add-claude-documentation-B8bmp

# Copy to the new repo
cp -r urban-resilience-sim/ ../urban-resilience-sim-standalone
cd ../urban-resilience-sim-standalone
rm -rf __pycache__

# Init and push
git init && git checkout -b main
echo -e "__pycache__/\n*.pyc" > .gitignore
git add . && git commit -m "Initial commit: Urban Resilience Simulator"
git remote add origin <https://github.com/JinnZ2/urban-resilience-sim.git>
git push -u origin main
