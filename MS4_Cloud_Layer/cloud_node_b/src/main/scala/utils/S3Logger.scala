package utils

import actors.RegionActor

object S3Logger {
  def write(region: String, update: RegionActor.DeviceUpdate): Unit = {
    // TODO: implement S3 logging
    println(s"[S3] Would log aggregated data for region $region")
  }
}
