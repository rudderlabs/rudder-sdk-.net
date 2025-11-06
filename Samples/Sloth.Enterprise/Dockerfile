#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

FROM mcr.microsoft.com/dotnet/core/runtime:2.1-stretch-slim@sha256:ea0a74b6a3804708cab2dd72caa6f9d58240dd862d7bccd748018d368ba8efe2 AS base
WORKDIR /app

FROM mcr.microsoft.com/dotnet/core/sdk:2.1-stretch@sha256:ae4daaaab45c6c6b0d2e36d93d8eed8ab255bdab9df02f08f3c39ba90ceb22a9 AS build
WORKDIR /src
COPY ["Samples/Sloth.Enterprise/Sloth.Enterprise.csproj", "Samples/Sloth.Enterprise/"]
COPY ["Samples/Sloth.Common/Sloth.Common.csproj", "Samples/Sloth.Common/"]
RUN dotnet restore "Samples/Sloth.Enterprise/Sloth.Enterprise.csproj"
COPY . .
WORKDIR "/src/Samples/Sloth.Enterprise"
RUN dotnet build "Sloth.Enterprise.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "Sloth.Enterprise.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Sloth.Enterprise.dll"]