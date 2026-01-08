package utils

import actors.RegionActor

object DynamoDBClient {
  def store(region: String, update: RegionActor.DeviceUpdate): Unit = {
    // TODO: implement DynamoDB write
    println(s"[DynamoDB] Would store reading for region $region, device ${update.deviceId}")
  }
}
