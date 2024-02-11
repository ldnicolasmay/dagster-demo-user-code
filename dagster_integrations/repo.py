import os
from collections import Counter

from dagster import In, config_from_files, file_relative_path, graph, op, repository
# from dagster_aws.s3 import s3_pickle_io_manager, s3_resource
from dagster_gcp.gcs import gcs_pickle_io_manager, gcs_resource
# from dagster_celery_k8s import celery_k8s_job_executor
from dagster_k8s import k8s_job_executor

from dagster import get_dagster_logger  # TODO: new


@op(ins={"word": In(str)}, config_schema={"factor": int})
def multiply_the_word(context, word):
    get_dagster_logger().info(f"context.resources={context.resources}")
    return word * context.op_config["factor"]


@op(ins={"word": In(str)})
def count_letters(word):
    return dict(Counter(word))


@graph
def example_graph():
    count_letters(multiply_the_word())


example_job = example_graph.to_job(
    name="example_job",
    description="Example job. Use this to test your deployment.",
    config=config_from_files(
        [
            # file_relative_path(__file__, os.path.join("..", "run_config", "pipeline.yaml")),
            file_relative_path(__file__, os.path.join("run_config", "pipeline.yaml")),
        ]
    ),
)


pod_per_op_job = example_graph.to_job(
    name="pod_per_op_job",
    description="""
    Example job that uses the `k8s_job_executor` to run each op in a separate pod.

    **NOTE:** this job uses the s3_pickle_io_manager, which requires
    [AWS credentials](https://docs.dagster.io/deployment/guides/aws#using-s3-for-io-management).
    """,
    # resource_defs={"s3": s3_resource, "io_manager": s3_pickle_io_manager},
    resource_defs={"gcs": gcs_resource, "io_manager": gcs_pickle_io_manager},
    executor_def=k8s_job_executor,
    config=config_from_files(
        [
            # file_relative_path(__file__, os.path.join("..", "run_config", "k8s.yaml")),
            # file_relative_path(__file__, os.path.join("..", "run_config", "pipeline.yaml")),
            file_relative_path(__file__, os.path.join("run_config", "k8s.yaml")),
            file_relative_path(__file__, os.path.join("run_config", "pipeline.yaml")),
        ]
    ),
)

# pod_per_op_celery_job = example_graph.to_job(
#     name="pod_per_op_celery_job",
#     description="""
#     Example job that uses the `celery_k8s_job_executor` to send ops to Celery workers, which
#     launch them in individual pods.
#
#     **NOTE:** this job uses the s3_pickle_io_manager, which
#     requires [AWS credentials](https://docs.dagster.io/deployment/guides/aws#using-s3-for-io-management).
#     It also requires enabling the [CeleryK8sRunLauncher](https://docs.dagster.io/deployment/guides/kubernetes/deploying-with-helm-advanced) in the Helm
#     chart.
#     """,
#     resource_defs={"s3": s3_resource, "io_manager": s3_pickle_io_manager},
#     executor_def=celery_k8s_job_executor,
#     config=config_from_files(
#         [
#             file_relative_path(__file__, os.path.join("..", "run_config", "celery_k8s.yaml")),
#             file_relative_path(__file__, os.path.join("..", "run_config", "pipeline.yaml")),
#         ]
#     ),
# )


@op(
    ins={"word": In(str)},
    config_schema={"factor": int},
    tags={
        "dagster-k8s/config": {
            "container_config": {
                "resources": {
                    "requests": {"cpu": "1", "memory": "1Gi"},  # Scale up container resources
                }
            },
        }
    }
)
def multiply_the_word_2(context, word):
    get_dagster_logger().info(f"context.resources={context.resources}")
    return word * context.op_config["factor"]


@graph
def example_graph_2():
    count_letters(multiply_the_word_2())


pod_per_op_job_2 = example_graph_2.to_job(
    name="pod_per_op_job_2",
    description="""
    Example job that uses the `k8s_job_executor` to run each op in a separate pod.

    **NOTE:** this job uses the gcs_pickle_io_manager, which requires
    [GCS credentials](https://docs.dagster.io/deployment/guides/gcp#using-gcs-for-io-management).
    """,
    resource_defs={"gcs": gcs_resource, "io_manager": gcs_pickle_io_manager},
    executor_def=k8s_job_executor,
    config=config_from_files(
        [
            file_relative_path(__file__, os.path.join("run_config", "k8s.yaml")),
            file_relative_path(__file__, os.path.join("run_config", "pipeline_2.yaml")),
        ]
    ),
    tags={
        "dagster-k8s/config": {
            "job_spec_config": {
                "ttl_seconds_after_finished": 600
            }
        }
    },
)



@repository
def example_repo():
    # return [example_job, pod_per_op_job, pod_per_op_celery_job]
    # return [example_job]
    # return [example_job, pod_per_op_job]
    return [example_job, pod_per_op_job, pod_per_op_job_2]
