package utils

import play.api.libs.json._

object CropRecommender {

  case class CropSuggestion(crop: String, score: Double)

  def recommend(json: JsValue): List[CropSuggestion] = {
    val n = (json \ "N").as[Double]
    val p = (json \ "P").as[Double]
    val k = (json \ "K").as[Double]
    val ph = (json \ "ph").as[Double]

    List(
      CropSuggestion("Wheat",  score = 1.0 - math.abs(n - 90)/100),
      CropSuggestion("Rice",   score = 1.0 - math.abs(ph - 6.5)/10),
      CropSuggestion("Corn",   score = 1.0 - math.abs(k - 40)/50)
    ).sortBy(-_.score)
  }
}
