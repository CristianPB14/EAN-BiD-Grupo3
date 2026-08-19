# S3 · Nivel 2 · Comparación de factores de réplica

```bash
# Repetir para factor 1, 2 y 3
docker compose exec namenode hdfs dfs -D dfs.replication=<R> -D dfs.blocksize=1048576 \
  -put /muestra/muestra.csv /datos/muestra_r<R>.csv

docker compose exec namenode hdfs dfs -du -h /datos
docker compose exec namenode hdfs fsck /datos/muestra_r<R>.csv -files -blocks
```

| Archivo | Factor (R) | Tamaño Lógico | Tamaño Físico (Ocupado) | ¿Coincide con Lógico × R? |
| :--- | :---: | :--- | :--- | :--- |
| `muestra_r1.csv` | 1 | 9.9 M | 9.9 M | Sí |
| `muestra_r2.csv` | 2 | 9.9 M | 19.8 M | Sí |
| `muestra_r3.csv` | 3 | 9.9 M | 29.6 M | Sí |

> Referencia teórica del caso del acueducto (sesión 3, no reemplaza la medición propia): con 7,8 GB
> lógicos, R=1 → 7,8 GB, R=2 → 15,6 GB, R=3 → 23,4 GB.

## Prueba de pérdida con factor 1

java.nio.channels.UnresolvedAddressException
        at sun.nio.ch.Net.checkAddress(Net.java:101)
        at sun.nio.ch.SocketChannelImpl.connect(SocketChannelImpl.java:622)
        at org.apache.hadoop.net.SocketIOWithTimeout.connect(SocketIOWithTimeout.java:192)
        at org.apache.hadoop.net.NetUtils.connect(NetUtils.java:533)
        at org.apache.hadoop.hdfs.DFSClient.newConnectedPeer(DFSClient.java:2940)
        at org.apache.hadoop.hdfs.client.impl.BlockReaderFactory.nextTcpPeer(BlockReaderFactory.java:822)
        at org.apache.hadoop.hdfs.client.impl.BlockReaderFactory.getRemoteBlockReaderFromTcp(BlockReaderFactory.java:747)
        at org.apache.hadoop.hdfs.client.impl.BlockReaderFactory.build(BlockReaderFactory.java:380)
        at org.apache.hadoop.hdfs.DFSInputStream.getBlockReader(DFSInputStream.java:644)
        at org.apache.hadoop.hdfs.DFSInputStream.blockSeekTo(DFSInputStream.java:575)
        at org.apache.hadoop.hdfs.DFSInputStream.readWithStrategy(DFSInputStream.java:757)
        at org.apache.hadoop.hdfs.DFSInputStream.read(DFSInputStream.java:829)
        at java.io.DataInputStream.read(DataInputStream.java:100)
        at org.apache.hadoop.io.IOUtils.copyBytes(IOUtils.java:94)
        at org.apache.hadoop.io.IOUtils.copyBytes(IOUtils.java:68)
        at org.apache.hadoop.io.IOUtils.copyBytes(IOUtils.java:129)
        at org.apache.hadoop.fs.shell.Display$Cat.printToStdout(Display.java:101)
        at org.apache.hadoop.fs.shell.Display$Cat.processPath(Display.java:96)
        at org.apache.hadoop.fs.shell.Command.processPathInternal(Command.java:367)
        at org.apache.hadoop.fs.shell.Command.processPaths(Command.java:331)
        at org.apache.hadoop.fs.shell.Command.processPathArgument(Command.java:304)
        at org.apache.hadoop.fs.shell.Command.processArgument(Command.java:286)
        at org.apache.hadoop.fs.shell.Command.processArguments(Command.java:270)
        at org.apache.hadoop.fs.shell.FsCommand.processRawArguments(FsCommand.java:120)
        at org.apache.hadoop.fs.shell.Command.run(Command.java:177)
        at org.apache.hadoop.fs.FsShell.run(FsShell.java:327)
        at org.apache.hadoop.util.ToolRunner.run(ToolRunner.java:76)
        at org.apache.hadoop.util.ToolRunner.run(ToolRunner.java:90)
        at org.apache.hadoop.fs.FsShell.main(FsShell.java:390)

## Relación factor–tolerancia, con números propios

`COMPLETAR` — expresen la relación con las cifras que acaban de medir, no como impresión general.
