package actors
import akka.actor.typed.{ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors
import play.api.libs.json._

object GlobalCoordinatorActor {

  sealed trait Command
  case class IncomingCloudEvent(deviceId: String, region: String, json: JsValue) extends Command
  case class RegionSummary(region: String, update: RegionActor.DeviceUpdate) extends Command

  def apply(): Behavior[Command] =
    Behaviors.setup { ctx =>
      implicit val system = ctx.system
      var regionActors = Map.empty[String, ActorRef[RegionActor.Command]]
      
      Behaviors.receiveMessage {
        case IncomingCloudEvent(deviceId, region, json) =>
          val regionActor = regionActors.getOrElse(region, {
            val ra = ctx.spawn(RegionActor(region, ctx.self), s"region-$region")
            regionActors += region -> ra
            ra
          })
          regionActor ! RegionActor.Process(deviceId, json)
          Behaviors.same

        case RegionSummary(region, update) =>
          println(s"[GLOBAL] Summary for $region → ${update.deviceId}")
          Behaviors.same
      }
    }
}
