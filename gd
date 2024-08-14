variable "access_entries" {
  description = "Defines the ARNs for cluster admins, editors, and viewers along with their respective namespaces."
  type = object({
    clusteradmins = list(string)
    clustereditors = list(object({
      arn        = string
      namespaces = list(string)
    }))
    clusterviewers = list(object({
      arn        = string
      namespaces = list(string)
    }))
  })
  default = {
    clusteradmins = ["clusteradmin-arn-one", "clusteradmin-arn-two"]
    clustereditors = [
      {
        arn        = "clustereditor-arn-one"
        namespaces = ["namespace1", "namespace2"]
      },
      {
        arn        = "clustereditor-arn-two"
        namespaces = ["namespace3"]
      }
    ]
    clusterviewers = [
      {
        arn        = "clusterviewer-arn-one"
        namespaces = ["namespace1"]
      },
      {
        arn        = "clusterviewer-arn-two"
        namespaces = []
      }
    ]
  }
}

# Example input
locals {
  access_entries = {
    clusteradmins = ["clusteradmin-arn-one", "clusteradmin-arn-two"]
    clustereditors = [
      {
        arn        = "clustereditor-arn-one"
        namespaces = []
      },
      {
        arn        = "clustereditor-arn-two"
        namespaces = []
      }
    ]
    clusterviewers = [
      {
        arn        = "clusterviewer-arn-one"
        namespaces = []
      },
      {
        arn        = "clusterviewer-arn-two"
        namespaces = []
      }
    ]
  }

  local_partition = "aws"
}

locals {
  # Cluster Admins
  cluster_admins = {
    for i, arn in local.access_entries.clusteradmins :
    "clusteradmin_${i + 1}" => {
      principal_arn     = arn
      type              = "STANDARD"
      kubernetes_groups = ["cluster-admins"]
      policy_associations = {
        admin = {
          policy_arn = "arn:${local.local_partition}:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }

  # Cluster Editors
  cluster_editors = {
    for i, editor in local.access_entries.clustereditors :
    "clustereditor_${i + 1}" => {
      principal_arn = editor.arn
      type          = "STANDARD"
      policy_associations = {
        clustereditor = {
          policy_arn = "arn:${local.local_partition}:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"
          access_scope = {
            namespaces = editor.namespaces
          }
        }
      }
    }
  }

  # Cluster Viewers
  cluster_viewers = {
    for i, viewer in local.access_entries.clusterviewers :
    "clusterviewer_${i + 1}" => {
      principal_arn = viewer.arn
      type          = "STANDARD"
      policy_associations = {
        clustereditor = {
          policy_arn = "arn:${local.local_partition}:eks::aws:cluster-access-policy/AmazonEKSViewPolicy"
          access_scope = {
            namespaces = viewer.namespaces
          }
        }
      }
    }
  }

  # Combine all roles into a single local variable
  combined_roles = merge(local.cluster_admins, local.cluster_editors, local.cluster_viewers)
}

# Output the configuration (optional, for visualization)
output "generated_config" {
  value = local.combined_roles
}
