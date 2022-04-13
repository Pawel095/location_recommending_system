import subprocess
import tarfile
import pyspark as pyspark_
from pyspark import SparkConf, SparkContext
from os.path import abspath, dirname, join, isfile
from os import listdir, makedirs, remove, walk
import shutil
import glob

DOWNLOAD_JARS = [
    "org.apache.sedona:sedona-python-adapter-3.0_2.12:1.1.1-incubating",
    "org.apache.sedona:sedona-viz-3.0_2.12:1.1.1-incubating",
    "org.datasyslab:geotools-wrapper:1.1.0-25.2",
]
HADOOP_JARS_PATH = "/spark"
HDFS_PATH = "/opt/hadoop-3.2.3/bin/hdfs"


base_dir = abspath(join(dirname(abspath(__file__)), "..", ".."))
ivyJarsCache = join(base_dir, "ivyJarsCache")

ivyJarsPath = join(ivyJarsCache, "jars")
sparkJarsPath = join(dirname(abspath(pyspark_.__file__)), "jars")

tempJarDir = join(base_dir, "jars/")
jarsArchive = join(base_dir, "jars.tar")


def gather_jars():
    all_jars = []
    for f in glob.glob(ivyJarsCache+"/**/.jar",recursive=True):
        all_jars.append(f)
    for f in listdir(sparkJarsPath):
        all_jars.append(join(sparkJarsPath, f))

    makedirs(tempJarDir, exist_ok=True)
    for f in all_jars:
        shutil.copy(f, tempJarDir)

    with tarfile.open(jarsArchive, "w") as tf:
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


def run():
    print("Downloading...")
    download_jars()
    print("Gathering...")
    gather_jars()
    print("Done!")


if __name__ == "__main__":
    run()
