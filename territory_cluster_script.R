#Simple Territory Clustering Script for use with Tableau Prep
#Author : Hunter Barcello [hbarcello@gmail.com or hbarcello@tableau.com]
#For 2019 Tableau Conference "Optimizing Sales Territories with Tableau"

#Test Script (The commented out portions are just for testing outside of Prep)

#main.df <- For_R_Input # Replace "For_R_Input" with your input file

#colnames(main.df) <- c("DesiredTerritories","Postal", "State", "Index", "Latitude", "Longitude")



#Before running this script the user will need to determine their desired number of territories
#and insert that as a field named "DesiredTerritories" in their prep workflow
#--Remember to remove all NULL latitude and longitude values before clustering!--

postal_cluster <- function(main.df){
  
  #Guess territory target size using Index:Territory ratio
  
  target.mean <- sum(main.df$Index)/main.df$Territories
  #target cluster size (sets size as a proporation of target.mean
  #example, cluster size of .10 will average 10 clusters per territory)
  target.cluster.size = .08
  
  main.df <- main.df[main.df$Index < target.mean*.70,]
  state_list <- unique(main.df$State)
  
  #Creating temporary vectors that we will use inside the loop for each state
  x_temp <- numeric()
  y_temp <- numeric()
  State <- character()
  Cluster <- character()
  key_temp <- character()
  index_temp <- numeric()
  output.df <- data.frame(CentroidX = double(), CentroidY = double(), 
                          State = character(), Key = character(), 
                          Index = numeric())
  Cluster <- character(0)
  
  
  #Iterate through each unique state
  for(s in state_list){
    #Select only records with same state
    temp.df <- subset(main.df, State==s, select=c(Latitude, Longitude, Postal, 
                                                  Index))
    
    #calculate average index of a postal code in the state
    state.mean <- mean(temp.df$Index)
    
    #Some guesses at what an appropriate number of clusters might be
    #Always have at least 2 clusters in a State for some flexibility
    num.clust <- round(nrow(temp.df)/((target.mean*target.cluster.size)/state.mean))
    if(num.clust < 2){ num.clust=2 } else {num.clust}
    
    #create a vector representing which state this is
    #Only doing this so we can keep the information intact when we write the data
    State <- c(State, rep(s, times=nrow(temp.df)))
    
    #Store key and x,y coords in this vector to add back in at the end
    x_temp <- c(x_temp, temp.df$Latitude)
    y_temp <- c(y_temp, temp.df$Longitude)
    key_temp <- as.character(c(key_temp, temp.df$Postal))
    index_temp <- c(index_temp, temp.df$Index)
    
    temp.df$CentroidX <- as.numeric(temp.df$Latitude)
    temp.df$CentroidY <- as.numeric(temp.df$Longitude)
    
    kclust <- kmeans(temp.df[,c("Latitude", "Longitude")], num.clust[1], iter.max=10)
    temp.df$cluster_assign_kmed <- paste(s, kclust$cluster)
    
    #Create information on clusters and their values (Summary Table)
    cluster.agg.value <- aggregate(Index ~ cluster_assign_kmed, data=temp.df, sum)
    
    #Remove Values that are lower than 100% target Index for a territory
    #First - create vector with cluster names to remove
    clusters.to.break <- cluster.agg.value[as.numeric(cluster.agg.value$Index) > as.numeric(target.mean), ]
    
    
    if(nrow(clusters.to.break) > 0){
      
      
      #Create new data frame to cluster again
      to.recluster <- temp.df[temp.df$cluster_assign_kmed %in% clusters.to.break$cluster_assign_kmed, ]
      
      num.clust2 <- min(round(sum(to.recluster$Index)/(as.numeric(target.mean)*.15)), nrow(to.recluster)/2) #Calculate New Number of Clusters for Secondary Stage
      if(num.clust2 < 2){ num.clust2 <- 2} #Just to make sure we don't get that cluster less than 2 error
      
      kmedclust2 <- kmeans(to.recluster[,1:2], num.clust2, iter.max=10)
      to.recluster$new.clust <- paste("Round2", s, kmedclust2$cluster)
      temp.df$cluster_assign_kmed[temp.df$cluster_assign_kmed %in% clusters.to.break$cluster_assign_kmed] <- to.recluster$new.clust
      
      
  
  
  }
  
  output.df <- rbind(output.df, data.frame(temp.df$Latitude, 
                                             temp.df$Longitude, 
                                             rep(s, times=nrow(temp.df)),
                                             temp.df$Postal, temp.df$Index, 
                                             temp.df$cluster_assign_kmed))
  
  
  
  }
  
  colnames(output.df) <- c("Latitude", "Longitude", "State", "Postal", "Index", "Cluster")
  
  
  
  return(data.frame(Latitude=output.df$Latitude, Longitude=output.df$Longitude, State=output.df$State, 
                    Postal=output.df$Postal, Index=output.df$Index, Cluster=output.df$Cluster))

  
  
  
  }

getOutputSchema <- function() {
  return (data.frame(
    Latitude = prep_decimal(),
    Longitude = prep_decimal(),
    State = prep_string(),
    Postal = prep_string(),
    Index = prep_string(),
    Cluster = prep_string()));
}
