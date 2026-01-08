package actors
import akka.actor.typed.{ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors
import play.api.libs.json._
import utils.{SoilClassifier, CropRecommender}

object RegionActor {

  sealed trait Command
  case class Process(deviceId: String, json: JsValue) extends Command

  case class DeviceUpdate(
      deviceId: String,
      soil: SoilClassifier.SoilQuality,
      crops: List[CropRecommender.CropSuggestion]
  )

  def apply(region: String, replyTo: ActorRef[GlobalCoordinatorActor.Command]): Behavior[Command] =
    Behaviors.receive { (ctx, message) =>
      message match {
        case Process(deviceId, json) =>
          val anomaly = (json \ "anomaly_result")
          val n  = (anomaly \ "N").asOpt[Double].getOrElse(50.0)
          val p  = (anomaly \ "P").asOpt[Double].getOrElse(50.0)
          val k  = (anomaly \ "K").asOpt[Double].getOrElse(50.0)
          val ph = (anomaly \ "ph").asOpt[Double].getOrElse(7.0)
          val syntheticJson = Json.obj(
            "N"  -> n,
            "P"  -> p,
            "K"  -> k,
            "ph" -> ph
          )
          val soil = SoilClassifier.classify(syntheticJson)
          val recs = CropRecommender.recommend(syntheticJson)
          println(s"[REGION $region] Soil quality = $soil")
          println(s"[REGION $region] Crop recommendations = $recs")
          replyTo ! GlobalCoordinatorActor.RegionSummary(
            region,
            DeviceUpdate(deviceId, soil, recs)
          )

          Behaviors.same
      }
    }
}
