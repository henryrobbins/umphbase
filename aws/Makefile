# Make the policy
policy:
	aws iam create-policy \
	--policy-name UmphbasePolicy \
	--description TODO \
	--policy-document file://configs/policy.json \

# Make the role
role:
	aws iam create-role \
	--role-name UmphbaseRole \
	--description TODO \
	--assume-role-policy-document file://configs/role.json