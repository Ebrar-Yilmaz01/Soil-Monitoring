import scalaj.http._
import actors.RegionActor
import play.api.libs.json._

object CloudRouter {
  val API_URL = "https://jw2b1cndwl.execute-api.us-east-1.amazonaws.com"

  def forwardToAWS(region: String, update: RegionActor.DeviceUpdate): Unit = {

    val bodyJson = Json.obj(
      "region" -> region,
      "deviceId" -> update.deviceId,
      "soil" -> update.soil.toString,
      "crops" -> update.crops.map(c => Json.obj(
        "crop" -> c.crop,
        "score" -> c.score
      ))
    )

    try {
      val response = Http(API_URL + "/cloud/update")
        .postData(bodyJson.toString())
        .header("Content-Type", "application/json")
        .timeout(connTimeoutMs = 5000, readTimeoutMs = 5000)
        .asString
      println(s"[Cloud → AWS] Response: ${response.code} ${response.body}")

    } catch {
      case e: Exception =>
        println(s"[Cloud → AWS] ERROR: ${e.getMessage}")
    }
  }
}
