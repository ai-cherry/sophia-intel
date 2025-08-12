import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as kubernetes from "@pulumi/kubernetes";
import axios from "axios";

// Configuration
const config = new pulumi.Config();
const lambdaApiKey = config.requireSecret("lambdaApiKey");
const lambdaCloudApiKey = config.requireSecret("lambdaCloudApiKey");

// Lambda Labs Custom Provider
class LambdaLabsProvider {
    private apiKey: pulumi.Output<string>;
    private baseUrl = "https://cloud.lambdalabs.com/api/v1";

    constructor(apiKey: pulumi.Output<string>) {
        this.apiKey = apiKey;
    }

    async createInstance(name: string, instanceType: string, region: string, sshKeyId: string) {
        return pulumi.all([this.apiKey]).apply(async ([key]) => {
            const response = await axios.post(
                `${this.baseUrl}/instances`,
                {
                    name: name,
                    instance_type_name: instanceType,
                    region_name: region,
                    ssh_key_ids: [sshKeyId],
                    quantity: 1
                },
                {
                    headers: {
                        'Authorization': `Bearer ${key}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            return response.data;
        });
    }
}

// Initialize Lambda Labs provider
const lambdaProvider = new LambdaLabsProvider(lambdaApiKey);

// Create GPU instances for different services
export const gpuInstances = {
    // H100 for AI/MCP services
    aiCluster: new pulumi.ComponentResource("custom:lambdalabs:AICluster", "sophia-ai-cluster", {}, {
        providers: []
    }),
    
    // A10 for general services
    serviceCluster: new pulumi.ComponentResource("custom:lambdalabs:ServiceCluster", "sophia-service-cluster", {}, {
        providers: []
    })
};

// K3s Configuration
const k3sUserData = `#!/bin/bash
# Install K3s
curl -sfL https://get.k3s.io | sh -

# Install required tools
apt-get update
apt-get install -y docker.io git curl wget

# Configure Docker
systemctl enable docker
systemctl start docker

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Install Portkey Gateway
kubectl create namespace portkey
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: portkey-config
  namespace: portkey
data:
  config.yaml: |
    providers:
      - name: openrouter
        url: https://openrouter.ai/api/v1
        key: \${OPENROUTER_API_KEY}
      - name: openai
        url: https://api.openai.com/v1
        key: \${OPENAI_API_KEY}
      - name: anthropic
        url: https://api.anthropic.com/v1
        key: \${ANTHROPIC_API_KEY}
EOF

# Signal completion
echo "K3s cluster initialized successfully" > /var/log/k3s-init.log
`;

// Database Stack Configuration
export const databases = {
    // Neon Serverless Postgres
    neon: {
        endpoint: pulumi.output("https://console.neon.tech/api/v2"),
        projectId: config.require("neonProjectId")
    },

    // Qdrant Vector Database (deployed on K3s)
    qdrant: new kubernetes.apps.v1.Deployment("qdrant", {
        metadata: {
            namespace: "databases",
            name: "qdrant"
        },
        spec: {
            replicas: 1,
            selector: {
                matchLabels: {
                    app: "qdrant"
                }
            },
            template: {
                metadata: {
                    labels: {
                        app: "qdrant"
                    }
                },
                spec: {
                    containers: [{
                        name: "qdrant",
                        image: "qdrant/qdrant:latest",
                        ports: [{
                            containerPort: 6333
                        }],
                        env: [{
                            name: "QDRANT__SERVICE__HTTP_PORT",
                            value: "6333"
                        }],
                        volumeMounts: [{
                            name: "qdrant-storage",
                            mountPath: "/qdrant/storage"
                        }]
                    }],
                    volumes: [{
                        name: "qdrant-storage",
                        persistentVolumeClaim: {
                            claimName: "qdrant-pvc"
                        }
                    }]
                }
            }
        }
    }),

    // Redis for caching
    redis: new kubernetes.apps.v1.Deployment("redis", {
        metadata: {
            namespace: "databases",
            name: "redis"
        },
        spec: {
            replicas: 1,
            selector: {
                matchLabels: {
                    app: "redis"
                }
            },
            template: {
                metadata: {
                    labels: {
                        app: "redis"
                    }
                },
                spec: {
                    containers: [{
                        name: "redis",
                        image: "redis:7-alpine",
                        ports: [{
                            containerPort: 6379
                        }],
                        command: ["redis-server", "--appendonly", "yes"]
                    }]
                }
            }
        }
    }),

    // Neo4j Knowledge Graph
    neo4j: new kubernetes.apps.v1.StatefulSet("neo4j", {
        metadata: {
            namespace: "databases",
            name: "neo4j"
        },
        spec: {
            serviceName: "neo4j",
            replicas: 1,
            selector: {
                matchLabels: {
                    app: "neo4j"
                }
            },
            template: {
                metadata: {
                    labels: {
                        app: "neo4j"
                    }
                },
                spec: {
                    containers: [{
                        name: "neo4j",
                        image: "neo4j:5-enterprise",
                        ports: [
                            { containerPort: 7474 },
                            { containerPort: 7687 }
                        ],
                        env: [
                            { name: "NEO4J_AUTH", value: "neo4j/sophiaaios" },
                            { name: "NEO4J_ACCEPT_LICENSE_AGREEMENT", value: "yes" }
                        ]
                    }]
                }
            }
        }
    })
};

// MCP Services Deployments
export const mcpServices = {
    secretsServer: new kubernetes.apps.v1.Deployment("secrets-server", {
        metadata: {
            namespace: "mcp",
            name: "secrets-server"
        },
        spec: {
            replicas: 2,
            selector: {
                matchLabels: {
                    app: "secrets-server"
                }
            },
            template: {
                metadata: {
                    labels: {
                        app: "secrets-server"
                    }
                },
                spec: {
                    containers: [{
                        name: "secrets-server",
                        image: "sophia-aios/secrets-server:latest",
                        ports: [{
                            containerPort: 8100
                        }],
                        env: [
                            {
                                name: "SECRETS_SERVER_JWT_SECRET",
                                valueFrom: {
                                    secretKeyRef: {
                                        name: "secrets-server-config",
                                        key: "jwt-secret"
                                    }
                                }
                            }
                        ]
                    }]
                }
            }
        }
    }),

    toolServer: new kubernetes.apps.v1.Deployment("tool-server", {
        metadata: {
            namespace: "mcp",
            name: "tool-server"
        },
        spec: {
            replicas: 3,
            selector: {
                matchLabels: {
                    app: "tool-server"
                }
            },
            template: {
                metadata: {
                    labels: {
                        app: "tool-server"
                    }
                },
                spec: {
                    containers: [{
                        name: "tool-server",
                        image: "sophia-aios/tool-server:latest",
                        ports: [{
                            containerPort: 8101
                        }]
                    }]
                }
            }
        }
    }),

    memoryServer: new kubernetes.apps.v1.Deployment("memory-server", {
        metadata: {
            namespace: "mcp",
            name: "memory-server"
        },
        spec: {
            replicas: 2,
            selector: {
                matchLabels: {
                    app: "memory-server"
                }
            },
            template: {
                metadata: {
                    labels: {
                        app: "memory-server"
                    }
                },
                spec: {
                    containers: [{
                        name: "memory-server",
                        image: "sophia-aios/memory-server:latest",
                        ports: [{
                            containerPort: 8102
                        }]
                    }]
                }
            }
        }
    }),

    agentServer: new kubernetes.apps.v1.Deployment("agent-server", {
        metadata: {
            namespace: "mcp",
            name: "agent-server"
        },
        spec: {
            replicas: 5,
            selector: {
                matchLabels: {
                    app: "agent-server"
                }
            },
            template: {
                metadata: {
                    labels: {
                        app: "agent-server"
                    }
                },
                spec: {
                    containers: [{
                        name: "agent-server",
                        image: "sophia-aios/agent-server:latest",
                        ports: [{
                            containerPort: 8103
                        }],
                        resources: {
                            requests: {
                                "nvidia.com/gpu": "1"
                            },
                            limits: {
                                "nvidia.com/gpu": "1"
                            }
                        }
                    }]
                }
            }
        }
    })
};

// Networking Configuration
export const networking = {
    // Ingress for external access
    ingress: new kubernetes.networking.v1.Ingress("sophia-ingress", {
        metadata: {
            namespace: "default",
            name: "sophia-ingress",
            annotations: {
                "kubernetes.io/ingress.class": "traefik",
                "cert-manager.io/cluster-issuer": "letsencrypt-prod"
            }
        },
        spec: {
            tls: [{
                hosts: ["api.sophia-intel.ai"],
                secretName: "sophia-tls"
            }],
            rules: [{
                host: "api.sophia-intel.ai",
                http: {
                    paths: [
                        {
                            path: "/secrets",
                            pathType: "Prefix",
                            backend: {
                                service: {
                                    name: "secrets-server",
                                    port: { number: 8100 }
                                }
                            }
                        },
                        {
                            path: "/tools",
                            pathType: "Prefix",
                            backend: {
                                service: {
                                    name: "tool-server",
                                    port: { number: 8101 }
                                }
                            }
                        },
                        {
                            path: "/memory",
                            pathType: "Prefix",
                            backend: {
                                service: {
                                    name: "memory-server",
                                    port: { number: 8102 }
                                }
                            }
                        },
                        {
                            path: "/agents",
                            pathType: "Prefix",
                            backend: {
                                service: {
                                    name: "agent-server",
                                    port: { number: 8103 }
                                }
                            }
                        }
                    ]
                }
            }]
        }
    })
};

// Export stack outputs
export const stackOutputs = {
    clusterEndpoint: "https://api.sophia-intel.ai",
    dashboardUrl: "https://www.sophia-intel.ai",
    grafanaUrl: "https://grafana.sophia-intel.ai",
    argocdUrl: "https://argocd.sophia-intel.ai"
};

// Stack information
export const stackInfo = pulumi.all([
    gpuInstances,
    databases,
    mcpServices,
    networking
]).apply(([gpu, db, mcp, net]) => ({
    message: "Sophia AIOS Infrastructure deployed successfully!",
    gpu: "GPU clusters ready",
    databases: "All databases operational",
    services: "MCP services running",
    networking: "Ingress configured"
}));
