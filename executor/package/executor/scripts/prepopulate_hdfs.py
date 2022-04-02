import subprocess
import tarfile
import pyspark as pyspark_
from pyspark import SparkConf, SparkContext
from os.path import abspath, dirname, join, isfile
from os import listdir, makedirs, remove
import shutil

DOWNLOAD_JARS = [
    "org.apache.sedona:sedona-python-adapter-3.0_2.12:1.1.1-incubating",
    "org.datasyslab:geotools-wrapper:1.1.0-25.2",
]
HADOOP_JARS_PATH = "/spark"
HDFS_PATH = "/opt/hadoop-3.2.3/bin/hdfs"


base_dir = abspath(join(dirname(abspath(__file__)), "..", ".."))
ivyJarsCache = join(base_dir, "ivyJarsCache")

ivyJarsPath = join(ivyJarsCache, "jars")
sparkJarsPath = join(dirname(abspath(pyspark_.__file__)), "jars")

tempJarDir = join(base_dir, "jars/")
jarsArchive = join(base_dir, "jars.tar.gz")


def gather_jars():
    all_jars = []
    for f in listdir(ivyJarsPath):
        all_jars.append(join(ivyJarsPath, f))
    for f in listdir(sparkJarsPath):
        all_jars.append(join(sparkJarsPath, f))

    makedirs(tempJarDir, exist_ok=True)
    for f in all_jars:
        shutil.copy(f, tempJarDir)

    with tarfile.open(jarsArchive, "w:gz") as tf:
        for f in listdir(tempJarDir):
            if isfile(join(tempJarDir, f)):
                tf.add(join(tempJarDir, f), arcname=f)


def download_jars():
    conf = (
        SparkConf()
        .set("spark.jars.packages", ",".join(DOWNLOAD_JARS))
        .set(
            "spark.driver.extraJavaOptions",
            f"-Divy.cache.dir={ivyJarsCache} -Divy.home={ivyJarsCache}",
        )
    )
    sc = SparkContext(conf=conf)
    sc.stop()


def upload_jars():
    mkdir = ["hdfs", "dfs", "-mkdir", "-p", HADOOP_JARS_PATH]
    up = [
        "hdfs",
        f"dfs",
        "-copyFromLocal",
        jarsArchive,
        HADOOP_JARS_PATH,
    ]
    subprocess.run(mkdir)
    subprocess.run(up)


def cleanup():
    print(f"shutil.rmtree({ivyJarsCache})")
    shutil.rmtree(ivyJarsCache)
    print(f"shutil.rmtree({tempJarDir[:-1]})")
    shutil.rmtree(tempJarDir[:-1])
    print(f"remove({jarsArchive})")
    remove(jarsArchive)


def run():
    print("Downloading...")
    download_jars()
    print("Gathering...")
    gather_jars()
    print("Uploading...")
    upload_jars()
    print("Cleanup...")
    cleanup()
    print("Done!")


if __name__ == "__main__":
    run()
