import akka.actor.typed.ActorSystem
import akka.actor.typed.scaladsl.Behaviors

object Main {

  def main(args: Array[String]): Unit = {
    implicit val system: ActorSystem[Nothing] =
      ActorSystem(Behaviors.empty, "CloudSystem")
    val coordinator =
      system.systemActorOf(actors.GlobalCoordinatorActor(), "global-coordinator")
    HttpServer.startHttpServer(coordinator)
    println("Cloud Node B started. Press ENTER to stop...")
    scala.io.StdIn.readLine()
  }
}
