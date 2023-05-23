
import unittest
from your_module import VaultAnnotationsGenerator

class TestVaultAnnotationsGenerator(unittest.TestCase):
    def setUp(self):
        items = {
            's3_general': True,
            'kafka_enabled': False,
            'redis_enabled': True
        }
        static_annotations = {
            'vault.hashicorp.com/agent-inject': 'true',
            'vault.hashicorp.com/namespace': '<<namespace_placeholder>>',
            'vault.hashicorp.com/role': '<<cluster_placeholder>>-<<namespace_placeholder>>-risk-app'
        }
        self.generator = VaultAnnotationsGenerator(items, static_annotations)

    def test_init(self):
        self.assertEqual(self.generator.items, {
            's3_general': True,
            'kafka_enabled': False,
            'redis_enabled': True
        })
        self.assertEqual(self.generator.annotations, {
            'vault.hashicorp.com/agent-inject': 'true',
            'vault.hashicorp.com/namespace': '<<namespace_placeholder>>',
            'vault.hashicorp.com/role': '<<cluster_placeholder>>-<<namespace_placeholder>>-risk-app'
        })
        self.assertEqual(self.generator.value_prefix, 'xxxxx')
        self.assertEqual(self.generator.s3_buckets, ['a', 'b'])

    def test_generate_annotations(self):
        self.generator.generate_annotations()

        # Check if the S3 secrets annotations are generated correctly
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-sec-s3-access'], 'xxxxx-access')
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-temp-s3-access'], '{{{- with secret "vault.hashicorp.com/agent-temp-s3-access - }}} {{ - range $n,$s := .Data.data -}}{{- $s -}}{{- end -}}{{- end -}}')
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-sec-s3-secret'], 'xxxxx-secret')
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-temp-s3-secret'], '{{{- with secret "vault.hashicorp.com/agent-temp-s3-secret - }}} {{ - range $n,$s := .Data.data -}}{{- $s -}}{{- end -}}{{- end -}}')

        # Check if the Redis secrets annotations are generated correctly
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-sec-redis-access'], 'xxxxx-access')
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-temp-redis-access'], '{{{- with secret "vault.hashicorp.com/agent-temp-redis-access - }}} {{ - range $n,$s := .Data.data -}}{{- $s -}}{{- end -}}{{- end -}}')
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-sec-redis-secret'], 'xxxxx-secret')
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-temp-redis-secret'], '{{{- with secret "vault.hashicorp.com/agent-temp-redis-secret - }}} {{ - range $n,$s := .Data.data -}}{{- $s -}}{{- end -}}{{- end -}}')

    def test_create_annotation(self):
        self.generator.create_annotation('s3-access', 'secret/data/myapp/s3-access')

        # Check if the secret and template annotations are created correctly
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-sec-s3-access'], 'secret/data/myapp/s3-access')
        self.assertEqual(self.generator.annotations['vault.hashicorp.com/agent-temp-s3-access'], '{{{- with secret "vault.hashic




class VaultAnnotationsGenerator:
    def __init__(self, static_annotations=None):
        """
        Initialize the class with static annotations.
        The input parameter static_annotations should be a dictionary where the keys are the annotation names and the
        values are the corresponding Vault secret paths.
        """
        self.annotations = static_annotations or {}

    def generate_annotations(self):
        """
        Generate annotations for S3, Kafka, and Redis secrets.
        """
        # S3 secrets
        s3_secret_path = 'secret/data/myapp/s3'
        s3_secret_annotation = f'vault.hashicorp.com/agent-inject-secret-s3/{s3_secret_path}'
        s3_template_annotation = f'vault.hashicorp.com/agent-inject-template-s3/{s3_secret_path}'
        self.annotations[s3_secret_annotation] = s3_secret_path
        self.annotations[s3_template_annotation] = s3_secret_path

        # Kafka secrets
        kafka_secret_path = 'secret/data/myapp/kafka'
        kafka_secret_annotation = f'vault.hashicorp.com/agent-inject-secret-kafka/{kafka_secret_path}'
        kafka_template_annotation = f'vault.hashicorp.com/agent-inject-template-kafka/{kafka_secret_path}'
        self.annotations[kafka_secret_annotation] = kafka_secret_path
        self.annotations[kafka_template_annotation] = kafka_secret_path

        # Redis secrets
        redis_secret_path = 'secret/data/myapp/redis'
        redis_secret_annotation = f'vault.hashicorp.com/agent-inject-secret-redis/{redis_secret_path}'
        redis_template_annotation = f'vault.hashicorp.com/agent-inject-template-redis/{redis_secret_path}'
        self.annotations[redis_secret_annotation] = redis_secret_path
        self.annotations[redis_template_annotation] = redis_secret_path

    def update_annotations(self, annotations_list):
        """
        Update the annotations dictionary with new annotations.
        The input parameter annotations_list should be a list of tuples where the first element of the tuple is the
        annotation name and the second element is the corresponding Vault secret path.
        """
        new_annotations = dict(annotations_list)
        self.annotations.update(new_annotations)

    def to_dict(self):
        """
        Convert the annotations to a dictionary that can be used to generate a deployment YAML.
        """
        annotations_dict = {}
        for key, value in self.annotations.items():
            annotations_dict[key] = value
        return annotations_dict

# Example usage:
static_annotations = {
    'vault.hashicorp.com/agent-inject-secret-static1': 'secret/data/myapp/static1',
    'vault.hashicorp.com/agent-inject-template-static1': 'secret/data/myapp/static1'
}
generator = VaultAnnotationsGenerator(static_annotations)
generator.generate_annotations()

new_annotations = [
    ('vault.hashicorp.com/agent-inject-secret-dynamic1', 'secret/data/myapp/dynamic1'),
    ('vault.hashicorp.com/agent-inject-template-dynamic1', 'secret/data/myapp/dynamic1'),
    ('vault.hashicorp.com/agent-inject-secret-dynamic2', 'secret/data/myapp/dynamic2'),
    ('vault.hashicorp.com/agent-inject-template-dynamic2', 'secret/data/myapp/dynamic2')
]
generator.update_annotations(new_annotations)

yaml_dict = {
    'apiVersion': 'apps/v1',
    'kind': 'Deployment',
    'metadata': {
        'name': 'my-deployment',
        'annotations': generator.to_dict()
    },
    'spec': {
        # ... deployment spec here ...
    }
}
