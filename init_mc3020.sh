#!/bin/bash

if [ ! -d "pyxtuml" ]; then
    git clone git@github.com:john-tornblom/pyxtuml.git
fi

if [ ! -d "mc" ]; then
    git clone git@github.com:xtuml/mc.git
fi


cat > run_mc3020.sh <<'EOF'
#!/bin/bash
SCRIPT_HOME=$(dirname $0)
MC_HOME=$SCRIPT_HOME/mc
PYXTUML_HOME=$SCRIPT_HOME/pyxtuml

export ROX_MC_ARC_DIR="."

if [ -z "$1" ]
  then
    echo "usage:" 
    echo "    $0 <path to bridgepoint project>"
exit 1
fi

MODEL_HOME=$1
MODEL_NAME=$(basename $MODEL_HOME)

$PYXTUML_HOME/gen_erate.py \
	--import $MC_HOME/model/com.mentor.nucleus.bp.core/src/xtumlmc_schema.sql \
	--import $MODEL_HOME/gen/code_generation/$MODEL_NAME.sql \
	--include $MODEL_HOME/gen \
	--include $MC_HOME/arc \
	--include $MC_HOME/arc/c \
	--include $MC_HOME/schema/colors \
	$MC_HOME/arc/c/sys.arc

EOF

chmod +x run_mc3020.sh


