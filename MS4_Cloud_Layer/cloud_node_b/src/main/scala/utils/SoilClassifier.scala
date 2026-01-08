package utils

import play.api.libs.json._

object SoilClassifier {

  case class SoilQuality(
    nLevel: String,
    pLevel: String,
    kLevel: String,
    phClass: String,
    fertility: String,
    overall: String
  )

  def classify(json: JsValue): SoilQuality = {
    val n = (json \ "N").as[Double]
    val p = (json \ "P").as[Double]
    val k = (json \ "K").as[Double]
    val ph = (json \ "ph").as[Double]

    def level(x: Double, low: Double, high: Double) =
      if (x < low) "Low" else if (x > high) "High" else "Medium"

    val quality = SoilQuality(
      nLevel = level(n, 50, 100),
      pLevel = level(p, 30, 60),
      kLevel = level(k, 40, 80),
      phClass = if (ph < 6) "Acidic" else if (ph > 8) "Alkaline" else "Neutral",
      fertility = "Moderate",
      overall = "Moderate"
    )

    quality
  }

  def toJson(q: SoilQuality): JsValue =
    Json.obj(
      "nLevel" -> q.nLevel,
      "pLevel" -> q.pLevel,
      "kLevel" -> q.kLevel,
      "phClass" -> q.phClass,
      "fertility" -> q.fertility,
      "overall" -> q.overall
    )
}
