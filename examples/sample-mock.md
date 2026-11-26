# Sample mock exam (original practice items for testing Study Buddy)

Question 1
A Jenkins pipeline must fail the build when code coverage drops below 80%. Which stage is the right place for this check?
A. Checkout
B. Quality gate after the test stage
C. Artifact upload
D. Post-deployment smoke test

Question 2
Which TWO actions make an Ansible playbook safe to run repeatedly? (Choose two)
A. Use modules that check state before changing it
B. Run every task with shell commands
C. Use changed_when and creates where a command is unavoidable
D. Disable fact gathering
E. Add ignore_errors to every task

Question 3
A web tier needs zero-downtime releases with an instant rollback path. Which strategy fits best?
A. Recreate deployment
B. Blue-green deployment
C. Manual patching in place
D. Nightly batch restart

Question 4
Where should a team store versioned build artifacts so that every environment deploys the same binary?
A. On each build agent's local disk
B. In the source repository
C. In an artifact repository such as Nexus
D. In the deployment server's temp folder

Answer Key
1. B Coverage is a quality signal, so it belongs in a gate after tests run.
2. A, C
3. B
4. C Build once, deploy the same artifact everywhere.
