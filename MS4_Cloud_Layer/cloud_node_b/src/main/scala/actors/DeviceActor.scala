package actors
import akka.actor.typed.{ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors
import play.api.libs.json.JsValue

object DeviceActor {

  sealed trait Command
  case class ProcessReading(json: JsValue, regionActor: ActorRef[RegionActor.Command]) extends Command

  def apply(deviceId: String): Behavior[Command] =
    Behaviors.receive { (ctx, message) =>
      message match {
        case ProcessReading(json, regionActor) =>
          regionActor ! RegionActor.Process(deviceId, json)
          Behaviors.same
      }
    }
}
