iqrf <- 2.5
outliers <- function(x) {
 q1 <- quantile(x, 0.25)
 q3 <- quantile(x, 0.75)
 iqr <- q3 - q1
 return(x<q1-iqr*iqrf | x>q3+iqr*iqrf)
}

myhist <- function(v, title) {
 if(sd(v)==0) {
  plot.new()
  return()
 }
 hist(v, main=paste("Histogram of", title), xlab=title)
 q1 <- quantile(v, 0.25)
 q3 <- quantile(v, 0.75)
 iqr <- q3 - q1
 abline(v=c(q1-iqr*iqrf, q3+iqr*iqrf), col="blue")
}

cells <- read.table("cells.dat", h=T)
good <- subset(cells, ! (outliers(a) | outliers(b) | outliers(c) | outliers(al) | outliers(be) | outliers(ga)))
write.table(good$file, "formerge_goodcell.lst", quote=F, row.names=F, col.names=F)

pdf("hist_cells.pdf", width=14, height=7)
par(mfrow=c(2,3))
myhist(cells$a, "a")
myhist(cells$b, "b")
myhist(cells$c, "c")
myhist(cells$al,"alpha")
myhist(cells$be,"beta")
myhist(cells$ga,"gamma")
dev.off()
cat("See hist_cells.pdf\n\n")

cat(sprintf("%4d files given.\n", nrow(cells)))
cat(sprintf("mean: %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n", mean(cells$a), mean(cells$b), mean(cells$c), mean(cells$al), mean(cells$be), mean(cells$ga)))
cat(sprintf(" std: %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n", sd(cells$a), sd(cells$b), sd(cells$c), sd(cells$al), sd(cells$be), sd(cells$ga)))
cat(sprintf(" iqr: %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n", IQR(cells$a), IQR(cells$b), IQR(cells$c), IQR(cells$al), IQR(cells$be), IQR(cells$ga)))

cat(sprintf("\n%4d files removed.\n", nrow(cells)-nrow(good)))
cat(sprintf("mean: %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n", mean(good$a), mean(good$b), mean(good$c), mean(good$al), mean(good$be), mean(good$ga)))
cat(sprintf(" std: %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n", sd(good$a), sd(good$b), sd(good$c), sd(good$al), sd(good$be), sd(good$ga)))
cat(sprintf(" iqr: %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n", IQR(good$a), IQR(good$b), IQR(good$c), IQR(good$al), IQR(good$be), IQR(good$ga)))

cat("\nUse formerge_goodcell.lst instead!\n")
