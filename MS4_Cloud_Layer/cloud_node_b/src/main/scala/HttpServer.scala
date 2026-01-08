import akka.actor.typed.ActorRef
import akka.actor.typed.ActorSystem
import akka.http.scaladsl.Http
import akka.http.scaladsl.server.Directives._
import scala.concurrent.ExecutionContextExecutor
import actors.GlobalCoordinatorActor
import play.api.libs.json._

object HttpServer {

  def startHttpServer(globalActor: ActorRef[GlobalCoordinatorActor.Command])
                     (implicit system: ActorSystem[_]): Unit = {

    implicit val ec: ExecutionContextExecutor = system.executionContext

    val route =
      path("alert") {
        post {
          entity(as[String]) { body =>
            val json = Json.parse(body)
            val deviceId = (json \ "device_id").as[String]
            val region = (json \ "edge_node").as[String]
            globalActor ! GlobalCoordinatorActor.IncomingCloudEvent(deviceId, region, json)
            complete("OK")
          }
        }
      }

    Http().newServerAt("0.0.0.0", 8080).bind(route)
    println("Cloud Node B HTTP server listening on port 8080")
  }
}
