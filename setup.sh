#
# file: setup.sh
# author: Ryan Reece <ryan.reece@cern.ch>
# created: August 17, 2012
#
# Basic setup script
#
###############################################################################


##-----------------------------------------------------------------------------
## pre-setup helpers, don't touch
##-----------------------------------------------------------------------------

#SVN_USER=${SVN_USER:-$USER} # set SVN_USER to USER if not set

path_of_this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
path_above_this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"
export MY_PROJECT=${path_of_this_dir}

add_to_python_path()
{
    export PYTHONPATH=$1:$PYTHONPATH
    echo "  Added $1 to your PYTHONPATH."
}

add_to_path()
{
    export PATH=$1:$PATH
    echo "  Added $1 to your PATH."
}

##-----------------------------------------------------------------------------
## install other packaages
##-----------------------------------------------------------------------------

## root2html
#if [ ! -d root2html ]; then
#    echo "  Checking-out root2html"
#    git clone https://github.com/rreece/root2html.git
#fi


##-----------------------------------------------------------------------------
## setup PYTHONPATH
##-----------------------------------------------------------------------------

echo "  Setting up your PYTHONPATH."
#add_to_python_path ${MY_PROJECT}
add_to_python_path ${MY_PROJECT}/package
#add_to_python_path ${MY_PROJECT}/../Spearmint
#add_to_python_path ${MY_PROJECT}/../simple_spearmint
echo "  done."


##-----------------------------------------------------------------------------
## setup PATH

#echo "  Setting up your PATH."
#add_to_path ${MY_PROJECT}
#add_to_path ${MY_PROJECT}/scripts
#echo "  done."



