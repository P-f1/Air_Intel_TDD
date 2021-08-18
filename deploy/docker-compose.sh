function deploy {

	DeployBaseFolder=$(pwd)
	ProjectBaseFolder=${DeployBaseFolder%/*}
	WorkingFolder=$DeployBaseFolder"/"$DeployType
	ArtifactsFolder=$ProjectBaseFolder"/artifacts/docker-compose/"$ServiceName
	Descriptor=$ProjectBaseFolder"/artifacts/docker-compose/"$ServiceName".yml"

	echo "BaseFolder="$DeployBaseFolder
	echo "WorkingFolder="$WorkingFolder
	echo "ArtifactsFolder="$ArtifactsFolder
	echo "PluginsFolder="$PluginsFolder
	echo "Descriptor="$Descriptor
	
	rm -rf ./$DeployType/$ServiceName
	mkdir -p ./$DeployType/$ServiceName

	cp -R $Descriptor ./$DeployType/$ServiceName
	
	if [ -f "$ArtifactsFolder" ]; then
		cp $ArtifactsFolder/* ./$DeployType/$ServiceName/$InstanceID
	fi

	cd ./$DeployType/$ServiceName
	echo "Deploy from $(pwd)"

	Mode=""
	if [ "y"==$DetachedMode ]
	then
		Mode="-d"
	fi

	if [ "k8s" == $DeployType ]; then
		kubectl apply -f .
	else
		if [[ -n $TargetServer ]]; then
			echo "Deploy Remotely !!"
			if [[ -n $Port ]]; then
				docker-compose -H "ssh://$Username@$TargetServer:$Port" rm -f
				#docker-compose --context $DockerContext up -d
				docker-compose -H "ssh://$Username@$TargetServer:$Port" up  -f $ServiceName".yml" $Mode --build
			else
				ls
				echo docker-compose -H "ssh://$Username@$TargetServer" rm  -f $ServiceName".yml" 
				#docker-compose --context $DockerContext up -d
				echo docker-compose -H "ssh://$Username@$TargetServer" -f $ServiceName".yml" up $Mode --build
			fi
		else
			echo "Deploy Locally !!"
			docker-compose rm -f
			docker-compose up -f $ServiceName".yml" $Mode --build
		fi
	fi
}

function undeploy {
	cd ./$DeployType/$ServiceName
	echo "Undeploy from $(pwd)"

	if [[ -n $TargetServer ]]; then
		echo "Undeploy Remotely !!"
		if [[ -n $Port ]]; then
			docker-compose -H "ssh://$Username@$TargetServer:$Port" -f $ServiceName".yml" down
			docker-compose -H "ssh://$Username@$TargetServer:$Port" rm -f
		else
			docker-compose -H "ssh://$Username@$TargetServer" -f $ServiceName".yml" down
			docker-compose -H "ssh://$Username@$TargetServer" rm -f
		fi
	else
		echo "Undeploy Locally !!"
		docker-compose -f $ServiceName".yml" down
		docker-compose rm -f
	fi
	
}