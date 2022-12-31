func main(){
   r := gin.Default()
   r.GET("/moreXML", func(c *gin.Context){
      type msg struct {
         Name string
         Message string
         Age int
      }
      var message msg
      message.Name="test"
      message.Message="Helloworld!"
      message.Age = 18
      c.XML(http.StatusOK,message)
   })
   r.Run(":8080")
}