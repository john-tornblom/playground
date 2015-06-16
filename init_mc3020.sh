#!/bin/bash

python -m pip install --user ply
python -m pip install --user pyxtuml
python -m pip install --user pyrsl

if [ ! -d "mc" ]; then
    git clone git@github.com:john-tornblom/mc.git -b pyrsl_fixes
fi


cat > run_mc3020.sh <<'EOF'
#!/bin/bash
SCRIPT_HOME=$(dirname $0)
MC_HOME=$SCRIPT_HOME/mc

export ROX_MC_ARC_DIR="."

if [ -z "$1" ]
  then
    echo "usage:" 
    echo "    $0 <path to bridgepoint project>"
exit 1
fi

MODEL_HOME=$1
MODEL_NAME=$(basename $MODEL_HOME)

python -m rsl.gen_erate \
	--import $MC_HOME/model/com.mentor.nucleus.bp.core/src/xtumlmc_schema.sql \
	--import $MODEL_HOME/gen/code_generation/$MODEL_NAME.sql \
	--include $MODEL_HOME/gen \
	--include $MC_HOME/arc \
	--include $MC_HOME/arc/c \
	--include $MC_HOME/schema/colors \
	$MC_HOME/arc/c/sys.arc

EOF

chmod +x run_mc3020.sh


