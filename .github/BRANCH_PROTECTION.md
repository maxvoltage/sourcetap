# Branch Protection Setup

To enable branch protection for the main branch:

1. Go to: https://github.com/maxvoltage/sourcetap/settings/branches
2. Click "Add rule" or "Add branch protection rule"
3. In "Branch name pattern", enter: `main`
4. Enable the following settings:
   - ✅ **Require a pull request before merging**
   - ✅ **Require status checks to pass before merging**
     - Search and add these required checks:
       - `Unit Tests`
       - `Integration Tests`
   - ✅ **Require branches to be up to date before merging**
5. Click "Create" or "Save changes"

This will ensure that both unit tests and integration tests must pass before any code can be merged to main.
