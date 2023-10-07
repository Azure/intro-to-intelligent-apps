FROM mcr.microsoft.com/dotnet/aspnet:7.0 AS base
WORKDIR /app
EXPOSE 5291
ENV ASPNETCORE_URLS=http://+:5291

FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
ARG configuration=Release
WORKDIR /src
COPY ["acs-sk-csharp.csproj", "."]
RUN dotnet restore "acs-sk-csharp.csproj"
COPY ["Program.cs", "."]
COPY ["Plugins/", "./Plugins/"]
RUN dotnet build "acs-sk-csharp.csproj" -c $configuration -o /app/build

FROM build AS publish
ARG configuration=Release
RUN dotnet publish "acs-sk-csharp.csproj" -c $configuration -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "acs-sk-csharp.dll"]
