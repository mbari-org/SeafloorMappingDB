Instructions for contributing to the SMDB project
=================================================

### Setting up your development system
 
1. Build a development system following 
   [these instructions](https://github.com/mbari-org/SeafloorMappingDB#install-a-local-development-system-using-docker).

2. Fork the repository after logging into GitHub by clicking on the Fork button at 
   https://github.com/mbari-org/SeafloorMappingDB

3. Recommended: Generate SSH keys on your development system following the instructions at 
   https://help.github.com/articles/generating-ssh-keys/

4. Rename the existing `origin` remote to `upstream`:

        cd $SMDB_HOME
        git remote rename origin upstream

5. Assign `origin` remote to your forked repository:

        git remote add -f origin <your_github_clone_url>

   Replace \<your_github_clone_url\> with "Copy to clipboard" from GitHub web site

### Contributing follows a [typical GitHub workflow](https://guides.github.com/introduction/flow/):

1. cd into your working directory, e.g.:

        cd $STOQS_HOME

2. Create a branch off of main for the new feature: 

        git checkout main
        git checkout -b <my_new_feature>

3. Work on your feature; add and commit as you write code and test it. (Creating a new 
   branch is not strictly necessary, but it makes it easy to isolate the changes from
   other changes that are to be merged into upstream.)

4. Push the new branch to your fork on GitHub:

        git push origin <my_new_feature>

6. Share your contribution with others by issuing a 
   [pull request](https://help.github.com/articles/using-pull-requests/): Click the 
   Pull Request button from your forked repository on GitHub

### Synchronizing with upstream

You should periodically pull changes to your workspace from the upstream remote.  These 
commands will synchronize your fork with upstream, including any local changes you have
committed:

    git checkout main
    git pull upstream main
    git push origin

After this you can use the GitHub web interface to visualize differences between your 
fork and upstream and submit a Pull Request.

If a lot of changes have happened upstream and you have local commits that you have 
not made public you may want to do a `rebase` instead of `merge`.  A `rebase` will 
replay your local changes on top of what is in upstream, e.g.:

    git fetch upstream
    git rebase upstream/main

or 
    `git rebase upstream/<branch_name>`, if a lot of upstream development is happening on another branch 

WARNING: This will rewrite commit history, so should only be done if your local commits 
have not been made public.

